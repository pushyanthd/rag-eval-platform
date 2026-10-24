"""Read-only dependency checks; model warm-up runs separately during startup."""

import asyncio
from pathlib import Path
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ragops.config import ConfigBundle, Settings
from ragops.persistence.models import Base
from ragops.retrieval.errors import RetrievalError
from ragops.retrieval.store import SqlAlchemySearchDataStore
from ragops.schemas import ReadinessStatus


class ReadinessProbe(Protocol):
    async def check(self) -> dict[str, ReadinessStatus]: ...


class DatabaseReadinessProbe:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        *,
        bundle: ConfigBundle,
        settings: Settings,
    ) -> None:
        self._sessions = sessions
        self._bundle = bundle
        self._settings = settings
        # Reject a misspelled target during startup instead of retrying it forever.
        if settings.readiness_dataset is not None:
            bundle.datasets.get(settings.readiness_dataset)
            bundle.variants.get(settings.readiness_variant)

    async def check(self) -> dict[str, ReadinessStatus]:
        try:
            async with self._sessions() as session:
                # LIMIT 0 verifies table/column availability and SELECT permissions
                # without scanning benchmark data or requiring any ingested rows.
                for table in Base.metadata.sorted_tables:
                    await session.execute(select(table).limit(0))
        except (SQLAlchemyError, OSError):
            return {"database": "unavailable"}

        checks: dict[str, ReadinessStatus] = {"database": "ok"}
        dataset = self._settings.readiness_dataset
        if dataset is None:
            return checks

        manifest = self._bundle.datasets.get(dataset)
        variant = self._bundle.variants.get(self._settings.readiness_variant)
        try:
            index = await SqlAlchemySearchDataStore(self._sessions).resolve_index(
                dataset_name=dataset,
                dataset_version=manifest.version,
                split=manifest.default_split,
                embedding_model=variant.dense.model if variant.dense is not None else None,
            )
        except (RetrievalError, SQLAlchemyError, OSError):
            return {**checks, "index": "unavailable"}
        checks["index"] = "ok"

        if variant.sparse is not None:
            path = self._settings.artifact_directory / "bm25" / index.bm25_artifact_hash
            try:
                await asyncio.to_thread(_check_sparse_files, path)
            except OSError:
                checks["artifacts"] = "unavailable"
            else:
                checks["artifacts"] = "ok"
        return checks


def _check_sparse_files(path: Path) -> None:
    # Full integrity verification happens when warm-up loads the index. Probes
    # only check that every file needed by the memory-mapped index remains readable.
    for filename in (
        "params.index.json",
        "vocab.index.json",
        "data.csc.index.npy",
        "indices.csc.index.npy",
        "indptr.csc.index.npy",
        "corpus.jsonl",
        "corpus.mmindex.json",
    ):
        with (path / filename).open("rb") as source:
            if not source.read(1):
                raise OSError("empty BM25 artifact")
