import asyncio
from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

import ragops.api as api_module
from ragops.api import create_app
from ragops.config import Settings, load_config_bundle
from ragops.contracts import RankedHit, SearchRequest, SearchResponse
from ragops.persistence import Base, create_engine, create_session_factory
from ragops.readiness import DatabaseReadinessProbe
from ragops.schemas import ReadinessStatus


class FakeProbe:
    def __init__(self) -> None:
        self.checks: dict[str, ReadinessStatus] = {"database": "ok"}
        self.error: Exception | None = None

    async def check(self) -> dict[str, ReadinessStatus]:
        if self.error is not None:
            raise self.error
        return self.checks


class WarmupSearch:
    def __init__(self) -> None:
        self.calls = 0
        self.release = asyncio.Event()

    async def search(self, request: SearchRequest) -> SearchResponse:
        self.calls += 1
        await self.release.wait()
        return SearchResponse(
            hits=(
                RankedHit(document_id="doc-a", title="Mars", text="Red planet", rank=1, score=1),
            ),
            timings=(),
            trace_id="a" * 32,
            variant_hash="b" * 64,
            index_fingerprint="c" * 64,
        )


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    configured = Settings(_env_file=None, environment="test")
    monkeypatch.setattr(api_module, "Settings", lambda: configured)
    return configured


def test_readiness_detects_an_outage_and_recovery_without_affecting_liveness(
    settings: Settings,
) -> None:
    probe = FakeProbe()
    application = create_app(Mock(), Mock(), readiness_probe=probe)
    with TestClient(application) as client:
        assert client.get("/readyz").status_code == 200
        probe.error = RuntimeError("postgresql://user:secret@private.example/db")
        failed = client.get("/readyz")
        assert failed.status_code == 503
        assert failed.json()["checks"]["dependencies"] == "unavailable"
        assert "secret" not in failed.text
        assert "private.example" not in failed.text
        assert failed.headers["cache-control"] == "no-store"
        assert client.get("/healthz").status_code == 200
        probe.error = None
        assert client.get("/readyz").status_code == 200
    assert client.get("/readyz").status_code == 503


def test_readiness_times_out_and_cancels_a_stalled_dependency(settings: Settings) -> None:
    settings.readiness_timeout_seconds = 0.01
    cancelled = False

    class StalledProbe:
        async def check(self) -> dict[str, ReadinessStatus]:
            nonlocal cancelled
            try:
                await asyncio.Event().wait()
            finally:
                cancelled = True
            return {"database": "ok"}

    application = create_app(Mock(), Mock(), readiness_probe=StalledProbe())
    with TestClient(application) as client:
        response = client.get("/readyz")
        assert response.status_code == 503
        assert response.json()["checks"]["dependencies"] == "timeout"
        assert cancelled


def test_readiness_requires_production_authentication(settings: Settings) -> None:
    settings.environment = "production"
    settings.api_key_hashes = ()
    application = create_app(Mock(), Mock(), readiness_probe=FakeProbe())
    with TestClient(application) as client:
        response = client.get("/readyz")
        assert response.status_code == 503
        assert response.json()["checks"]["authentication"] == "unavailable"
        assert client.get("/healthz").status_code == 200


def test_readiness_requires_initialized_services(settings: Settings) -> None:
    application = create_app(Mock(), Mock(), readiness_probe=FakeProbe())
    with TestClient(application) as client:
        application.state.evaluation_service = None
        response = client.get("/readyz")
        assert response.status_code == 503
        assert response.json()["checks"]["services"] == "unavailable"


def test_required_retrieval_warms_once_outside_probes(settings: Settings) -> None:
    settings.readiness_dataset = "fixture"

    async def exercise() -> None:
        search = WarmupSearch()
        probe = FakeProbe()
        application = create_app(search, Mock(), readiness_probe=probe)
        async with (
            application.router.lifespan_context(application),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=application), base_url="http://test"
            ) as client,
        ):
            response = await client.get("/readyz")
            assert response.status_code == 503
            assert response.json()["checks"]["retrieval_warmup"] == "pending"
            search.release.set()
            await application.state.readiness_warmup
            assert (await client.get("/readyz")).status_code == 200
            assert (await client.get("/readyz")).status_code == 200
            assert search.calls == 1
            probe.checks["artifacts"] = "unavailable"
            assert (await client.get("/readyz")).status_code == 503

    asyncio.run(exercise())


def test_shutdown_cancels_an_unfinished_warmup(settings: Settings) -> None:
    settings.readiness_dataset = "fixture"

    async def exercise() -> None:
        application = create_app(WarmupSearch(), Mock(), readiness_probe=FakeProbe())
        async with application.router.lifespan_context(application):
            task = application.state.readiness_warmup
            await asyncio.sleep(0)
            assert not task.done()
        assert task.cancelled()
        assert not application.state.started

    asyncio.run(exercise())


def test_database_probe_requires_schema_and_accepts_an_empty_migrated_database(
    tmp_path: Path,
) -> None:
    async def exercise() -> None:
        engine = create_engine(f"sqlite+aiosqlite:///{tmp_path / 'readiness.db'}")
        probe = DatabaseReadinessProbe(
            create_session_factory(engine),
            bundle=load_config_bundle(Path("config")),
            settings=Settings(_env_file=None),
        )
        try:
            assert await probe.check() == {"database": "unavailable"}
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
            assert await probe.check() == {"database": "ok"}
            async with engine.begin() as connection:
                await connection.execute(text("DROP TABLE jobs"))
            assert await probe.check() == {"database": "unavailable"}
        finally:
            await engine.dispose()

    asyncio.run(exercise())
