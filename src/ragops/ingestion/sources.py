"""Local and checksum-verified remote dataset materialization."""

import logging
import shutil
import stat
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from http.client import IncompleteRead
from pathlib import Path

from ragops.config import LocalDatasetManifest, RemoteDatasetManifest
from ragops.ingestion.hashing import hash_file

_logger = logging.getLogger(__name__)


def _download_archive(url: str, destination: Path) -> None:
    """Retry transient network failures without retaining partial bytes."""
    for attempt in range(3):
        try:
            with (
                destination.open("wb") as target,
                urllib.request.urlopen(url, timeout=60) as response,
            ):
                shutil.copyfileobj(response, target)
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError, IncompleteRead) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code != 429 and error.code < 500:
                raise
            if attempt == 2:
                raise
            _logger.warning("Dataset download interrupted; retrying (%s)", type(error).__name__)
            time.sleep(2 ** (attempt + 1))


class ChecksumMismatchError(ValueError):
    pass


def verify_checksum(path: Path, *, algorithm: str, expected: str) -> None:
    observed = hash_file(path, algorithm)
    if observed != expected:
        raise ChecksumMismatchError(
            f"checksum mismatch for {path.name}: expected {expected}, observed {observed}"
        )


def _extract_zip_safely(archive_path: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(root):
                raise ValueError(f"archive member escapes destination: {member.filename}")
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"archive contains a symbolic link: {member.filename}")
        archive.extractall(destination)


def _validate_beir_directory(path: Path) -> Path:
    required = (path / "corpus.jsonl", path / "queries.jsonl", path / "qrels")
    if not all(item.exists() for item in required):
        raise ValueError(f"directory does not contain a BEIR dataset: {path}")
    return path


def materialize_dataset(
    name: str,
    manifest: LocalDatasetManifest | RemoteDatasetManifest,
    download_root: Path,
) -> Path:
    if isinstance(manifest, LocalDatasetManifest):
        return _validate_beir_directory(manifest.path)

    download_root.mkdir(parents=True, exist_ok=True)
    archive_path = download_root / f"{name}-{manifest.checksum}.zip"
    if not archive_path.exists():
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=f"{name}-", suffix=".download", dir=download_root, delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
            _download_archive(manifest.url, temporary_path)
            verify_checksum(
                temporary_path,
                algorithm=manifest.checksum_algorithm,
                expected=manifest.checksum,
            )
            temporary_path.rename(archive_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    else:
        verify_checksum(
            archive_path,
            algorithm=manifest.checksum_algorithm,
            expected=manifest.checksum,
        )

    extraction_root = download_root / f"{name}-{manifest.checksum}"
    marker = extraction_root / ".complete"
    if not marker.is_file():
        extraction_root.mkdir(parents=True, exist_ok=True)
        _extract_zip_safely(archive_path, extraction_root)
        nested = extraction_root / name
        dataset_directory = _validate_beir_directory(nested if nested.is_dir() else extraction_root)
        marker.write_text(manifest.checksum, encoding="utf-8")
        return dataset_directory

    nested = extraction_root / name
    return _validate_beir_directory(nested if nested.is_dir() else extraction_root)
