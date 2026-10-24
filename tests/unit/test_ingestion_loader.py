import hashlib
import io
import urllib.error
import zipfile
from pathlib import Path

import pytest

import ragops.ingestion.sources as sources
from ragops.config import RemoteDatasetManifest
from ragops.contracts import SourceDocument
from ragops.ingestion.hashing import hash_dataset
from ragops.ingestion.loader import load_beir_dataset
from ragops.ingestion.sources import (
    ChecksumMismatchError,
    _extract_zip_safely,
    materialize_dataset,
    verify_checksum,
)

FIXTURE_DIRECTORY = Path(__file__).parents[2] / "fixtures" / "tiny-beir"


def test_loads_beir_fixture_and_filters_queries_to_split() -> None:
    dataset = load_beir_dataset(FIXTURE_DIRECTORY, split="test")

    assert [document.external_id for document in dataset.documents] == [
        "doc-a",
        "doc-b",
        "doc-c",
    ]
    assert [query.external_id for query in dataset.queries] == ["q-1", "q-2"]
    assert len(dataset.qrels) == 2
    assert len(hash_dataset(dataset)) == 64


def test_source_document_preserves_an_empty_beir_corpus_row() -> None:
    document = SourceDocument(external_id="117276", title="", text="")

    assert document.title == ""
    assert document.text == ""


def test_checksum_verification_rejects_modified_file(tmp_path: Path) -> None:
    archive = tmp_path / "dataset.zip"
    archive.write_bytes(b"dataset")
    checksum = hashlib.md5(b"dataset", usedforsecurity=False).hexdigest()

    verify_checksum(archive, algorithm="md5", expected=checksum)
    with pytest.raises(ChecksumMismatchError, match="checksum mismatch"):
        verify_checksum(archive, algorithm="md5", expected="0" * 32)


def test_archive_extraction_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "malicious.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("../escape.txt", "malicious")

    with pytest.raises(ValueError, match="escapes destination"):
        _extract_zip_safely(archive, tmp_path / "destination")


def test_download_retries_partial_transfers_without_corrupting_the_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as archive:
        archive.writestr("scifact/corpus.jsonl", "{}\n")
        archive.writestr("scifact/queries.jsonl", "{}\n")
        archive.writestr("scifact/qrels/test.tsv", "query-id\tcorpus-id\tscore\n")
    payload = data.getvalue()
    calls = 0
    delays: list[int] = []

    class InterruptedDownload(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            if self.tell() > 0:
                raise ConnectionResetError("connection reset")
            return super().read(10)

    def download(*args: object, **kwargs: object) -> io.BytesIO:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise urllib.error.URLError(ConnectionRefusedError())
        return InterruptedDownload(payload) if calls == 2 else io.BytesIO(payload)

    monkeypatch.setattr(sources.urllib.request, "urlopen", download)
    monkeypatch.setattr(sources.time, "sleep", delays.append)
    manifest = RemoteDatasetManifest(
        source="remote",
        version="test",
        license_name="Test",
        url="https://example.com/scifact.zip",
        checksum_algorithm="md5",
        checksum=hashlib.md5(payload, usedforsecurity=False).hexdigest(),
    )
    directory = materialize_dataset("scifact", manifest, tmp_path)
    assert (directory / "corpus.jsonl").read_text() == "{}\n"
    assert calls == 3
    assert delays == [2, 4]
    assert not list(tmp_path.glob("*.download"))


@pytest.mark.parametrize("code,expected_calls", [(404, 1), (503, 3)])
def test_failed_downloads_are_bounded_and_clean_up_partial_files(
    code: int, expected_calls: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def fail(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        raise urllib.error.HTTPError("https://example.com", code, "failed", {}, None)

    monkeypatch.setattr(sources.urllib.request, "urlopen", fail)
    monkeypatch.setattr(sources.time, "sleep", lambda _: None)
    manifest = RemoteDatasetManifest(
        source="remote",
        version="test",
        license_name="Test",
        url="https://example.com/scifact.zip",
        checksum_algorithm="md5",
        checksum="a" * 32,
    )
    with pytest.raises(urllib.error.HTTPError):
        materialize_dataset("scifact", manifest, tmp_path)
    assert calls == expected_calls
    assert not list(tmp_path.iterdir())
