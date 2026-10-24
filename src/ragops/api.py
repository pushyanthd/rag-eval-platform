"""HTTP API for ragops."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncEngine

from ragops.artifact_store import ArtifactStore, build_artifact_store
from ragops.config import Settings, load_config_bundle
from ragops.contracts import (
    AnswerRequest,
    AnswerResponse,
    EvalRun,
    EvalRunSpec,
    SearchRequest,
    SearchResponse,
)
from ragops.evaluation import DatabaseEvaluationService, EvaluationService
from ragops.generation.factory import build_answer_service
from ragops.generation.service import AnswerService
from ragops.persistence import create_engine, create_session_factory
from ragops.provenance import resolve_git_commit, resolve_image_digest
from ragops.readiness import DatabaseReadinessProbe, ReadinessProbe
from ragops.retrieval.errors import (
    ArtifactNotFoundError,
    CompatibleIndexNotFoundError,
    DatasetNotIngestedError,
    RetrievalLimitError,
)
from ragops.retrieval.factory import build_retrieval_pipeline
from ragops.retrieval.pipeline import SearchExecutor
from ragops.schemas import HealthResponse, ReadinessResponse, ReadinessStatus
from ragops.security import ApiKeyAuthenticator
from ragops.telemetry import configure_telemetry, instrument_fastapi, prometheus_response

_logger = logging.getLogger(__name__)


def create_app(
    search_service: SearchExecutor | None = None,
    evaluation_service: EvaluationService | None = None,
    answer_service: AnswerService | None = None,
    *,
    artifact_store: ArtifactStore | None = None,
    readiness_probe: ReadinessProbe | None = None,
) -> FastAPI:
    """Build the FastAPI application."""

    settings = Settings()
    configure_telemetry(settings)
    authenticator = ApiKeyAuthenticator(settings.api_key_hashes)
    api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    async def require_api_key(
        api_key: Annotated[str | None, Security(api_key_header)],
    ) -> None:
        if not authenticator.configured:
            if settings.environment == "production":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="API authentication is not configured",
                )
            return
        if not authenticator.accepts(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine: AsyncEngine | None = None
        warmup_task: asyncio.Task[None] | None = None
        needs_search = application.state.search_service is None
        needs_evaluation = application.state.evaluation_service is None
        needs_answer = application.state.answer_service is None
        try:
            if (
                needs_search
                or needs_evaluation
                or (needs_answer and settings.openai_api_key is not None)
                or application.state.readiness_probe is None
            ):
                configured_store = artifact_store or build_artifact_store(settings)
                await configured_store.hydrate_runtime()
                bundle = load_config_bundle(settings.configuration_directory)
                engine = create_engine(settings.database_url)
                sessions = create_session_factory(engine)
                if application.state.readiness_probe is None:
                    application.state.readiness_probe = DatabaseReadinessProbe(
                        sessions, bundle=bundle, settings=settings
                    )
                if needs_search:
                    application.state.search_service = build_retrieval_pipeline(
                        bundle,
                        sessions,
                        artifact_root=settings.artifact_directory,
                        device=settings.model_device,
                        model_cache_directory=settings.model_cache_directory,
                    )
                if needs_evaluation:
                    application.state.evaluation_service = DatabaseEvaluationService(
                        sessions,
                        datasets=bundle.datasets,
                        variants=bundle.variants,
                        git_commit=resolve_git_commit(),
                        image_digest=resolve_image_digest(),
                    )
                if needs_answer and settings.openai_api_key is not None:
                    assert application.state.search_service is not None
                    application.state.answer_service = build_answer_service(
                        bundle,
                        sessions,
                        search=application.state.search_service,
                        settings=settings,
                    )
            if settings.readiness_dataset is not None:
                warmup_task = asyncio.create_task(warm_retrieval(application))
            application.state.readiness_warmup = warmup_task
            application.state.started = True
            yield
        finally:
            application.state.started = False
            if warmup_task is not None:
                warmup_task.cancel()
                with suppress(asyncio.CancelledError):
                    await warmup_task
            if engine is not None:
                await engine.dispose()

    async def warm_retrieval(application: FastAPI) -> None:
        """Exercise the required route outside probes, retrying after ingestion."""
        assert settings.readiness_dataset is not None
        request = SearchRequest(
            query="readiness probe",
            dataset=settings.readiness_dataset,
            variant=settings.readiness_variant,
            k=1,
        )
        while True:
            try:
                async with asyncio.timeout(settings.readiness_warmup_timeout_seconds):
                    result = await application.state.search_service.search(request)
                    if not result.hits:
                        raise ValueError("readiness retrieval returned no documents")
                return
            except Exception as error:
                # Never include database URLs, provider responses, or exception text.
                _logger.warning("Retrieval warm-up unavailable (%s)", type(error).__name__)
                await asyncio.sleep(5)

    application = FastAPI(
        title="RAG Evaluation & Observability Platform",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.search_service = search_service
    application.state.evaluation_service = evaluation_service
    application.state.answer_service = answer_service
    application.state.readiness_probe = readiness_probe
    application.state.readiness_warmup = None
    application.state.started = False
    instrument_fastapi(application)

    @application.get("/healthz", tags=["operations"])
    async def health() -> HealthResponse:
        """Report whether the process is alive."""
        return HealthResponse(status="ok")

    @application.get("/readyz", tags=["operations"], responses={503: {"model": ReadinessResponse}})
    async def readiness(response: Response) -> ReadinessResponse:
        """Check live dependencies within the load balancer's probe deadline."""
        checks: dict[str, ReadinessStatus] = {}
        if not application.state.started:
            checks["startup"] = "pending"
        else:
            services_available = (
                application.state.search_service is not None
                and application.state.evaluation_service is not None
                and (
                    settings.openai_api_key is None or application.state.answer_service is not None
                )
            )
            checks["services"] = "ok" if services_available else "unavailable"
            if settings.environment == "production":
                checks["authentication"] = "ok" if authenticator.configured else "unavailable"
            probe: ReadinessProbe | None = application.state.readiness_probe
            if probe is None:
                checks["dependencies"] = "unavailable"
            else:
                try:
                    async with asyncio.timeout(settings.readiness_timeout_seconds):
                        checks.update(await probe.check())
                except TimeoutError:
                    checks["dependencies"] = "timeout"
                except Exception:
                    checks["dependencies"] = "unavailable"
            if settings.readiness_dataset is not None:
                task: asyncio.Task[None] | None = application.state.readiness_warmup
                checks["retrieval_warmup"] = (
                    "ok"
                    if (
                        task is not None
                        and task.done()
                        and not task.cancelled()
                        and task.exception() is None
                    )
                    else "pending"
                )
        ready = all(value == "ok" for value in checks.values())
        response.status_code = 200 if ready else 503
        response.headers["Cache-Control"] = "no-store"
        return ReadinessResponse(status="ok" if ready else "not_ready", checks=checks)

    @application.get(
        "/metrics",
        tags=["operations"],
        include_in_schema=False,
        dependencies=[Depends(require_api_key)],
    )
    async def metrics() -> Response:
        """Expose process and retrieval metrics for Prometheus."""
        return prometheus_response()

    @application.post("/v1/search", tags=["retrieval"], dependencies=[Depends(require_api_key)])
    async def search(request: SearchRequest) -> SearchResponse:
        service: SearchExecutor | None = application.state.search_service
        if service is None:
            raise HTTPException(status_code=503, detail="retrieval service is not initialized")
        try:
            return await service.search(request)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error.args[0])) from error
        except DatasetNotIngestedError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except CompatibleIndexNotFoundError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except ArtifactNotFoundError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except RetrievalLimitError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @application.post("/v1/answer", tags=["generation"], dependencies=[Depends(require_api_key)])
    async def answer(request: AnswerRequest) -> AnswerResponse:
        service: AnswerService | None = application.state.answer_service
        if service is None:
            raise HTTPException(
                status_code=503,
                detail="answer generation is unavailable; configure RAGOPS_OPENAI_API_KEY",
            )
        try:
            return await service.answer(request)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error.args[0])) from error
        except DatasetNotIngestedError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except CompatibleIndexNotFoundError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        except ArtifactNotFoundError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        except RetrievalLimitError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @application.post(
        "/v1/evals",
        tags=["evaluation"],
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[Depends(require_api_key)],
    )
    async def submit_evaluation(request: EvalRunSpec, response: Response) -> EvalRun:
        """Queue an evaluation run for a worker and return the created record.

        The API never executes an evaluation inside a request; it writes the run and
        its job in one transaction and returns immediately.
        """
        service: EvaluationService | None = application.state.evaluation_service
        if service is None:
            raise HTTPException(status_code=503, detail="evaluation service is not initialized")
        try:
            run = await service.submit(request)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error.args[0])) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        response.headers["Location"] = f"/v1/evals/{run.id}"
        return run

    @application.get(
        "/v1/evals/{run_id}", tags=["evaluation"], dependencies=[Depends(require_api_key)]
    )
    async def read_evaluation(run_id: UUID) -> EvalRun:
        """Report the current state and progress of one evaluation run."""
        service: EvaluationService | None = application.state.evaluation_service
        if service is None:
            raise HTTPException(status_code=503, detail="evaluation service is not initialized")
        try:
            return await service.get(run_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error.args[0])) from error

    return application


app = create_app()
