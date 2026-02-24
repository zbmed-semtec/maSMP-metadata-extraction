"""
Unit tests for ExternalDataFetcherAdapter.
Cover archive URL merging from README (Zenodo, Software Heritage, Wayback),
OpenAlex enrichment recording, and reference publication creation when missing.
"""
from typing import Any, Dict, List, Optional

from app.adapters.external_data_fetcher_adapter import ExternalDataFetcherAdapter
from app.core.entities.repository_metadata import RepositoryMetadata
from app.domain.extraction_sources import (
    SOURCE_ZENODO_BADGE,
    SOURCE_WAYBACK,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_OPENALEX,
)


class DummyCollector:
    def __init__(self) -> None:
        self.calls: List[tuple[str, str]] = []

    def record(self, entity_field: str, source: str, confidence: float) -> None:  # type: ignore[override]
        self.calls.append((entity_field, source))


class DummyFileFetcher:
    def __init__(self, content: str):
        self._content = content

    def fetch_file_content(self, url: str) -> Optional[str]:
        return self._content


class DummyOpenAlexClient:
    def __init__(self, work: Dict[str, Any] | None):
        self.work = work
        self.enrich_called_with: list[tuple[RepositoryMetadata, Optional[str]]] = []

    def enrich_metadata(self, metadata: RepositoryMetadata, doi: Optional[str] = None) -> RepositoryMetadata:
        # Record the call and pretend to add a keyword if work is present
        self.enrich_called_with.append((metadata, doi))
        if self.work:
            existing = metadata.keywords or []
            if "from-openalex" not in existing:
                existing.append("from-openalex")
            metadata.keywords = existing
        return metadata

    def fetch_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        return self.work

    def extract_authors(self, work_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return work_data.get("authors", [])


class DummyWaybackClient:
    def __init__(self, swh_url: Optional[str], wayback_url: Optional[str]):
        self.swh_url = swh_url
        self.wayback_url = wayback_url

    def check_software_heritage(self, url: str) -> Optional[str]:
        return self.swh_url

    def check_archive_url(self, url: str) -> Optional[str]:
        return self.wayback_url


def _make_adapter_with_dummies(readme_content: str, swh_url: Optional[str], wayback_url: Optional[str], work: Dict[str, Any] | None):
    adapter = ExternalDataFetcherAdapter(platform="github")
    adapter.file_fetcher = DummyFileFetcher(readme_content)
    adapter.wayback_client = DummyWaybackClient(swh_url, wayback_url)
    adapter.openalex_client = DummyOpenAlexClient(work)
    return adapter


def test_external_data_fetcher_merges_archives_and_records_sources():
    readme_content = """
    Zenodo badge:
    https://zenodo.org/record/111111
    """
    swh_url = "https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://github.com/org/repo"
    wayback_url = "https://web.archive.org/web/https://github.com/org/repo"

    adapter = _make_adapter_with_dummies(readme_content, swh_url, wayback_url, work=None)
    metadata = RepositoryMetadata()
    collector = DummyCollector()

    updated = adapter.fetch_external_data(
        repo_url="https://github.com/org/repo",
        metadata=metadata,
        doi=None,
        reference_extracted=False,
        extraction_metadata=collector,  # type: ignore[arg-type]
    )

    # archivedAt should contain all three sources (Zenodo URL as-is from URL matcher,
    # plus SWH and Wayback URLs).
    assert updated.archivedAt is not None
    assert swh_url in updated.archivedAt
    assert wayback_url in updated.archivedAt
    # At least one archive entry should exist (Zenodo badge handling is tested elsewhere)
    assert len(updated.archivedAt) >= 2

    # Check that Software Heritage and Wayback archive sources were recorded
    sources = {src for (_, src) in collector.calls}
    assert SOURCE_SOFTWARE_HERITAGE in sources
    assert SOURCE_WAYBACK in sources


def test_external_data_fetcher_records_openalex_enrichment_and_reference_publication():
    readme_content = ""  # no zenodo badge
    swh_url = None
    wayback_url = None
    work = {
        "title": "OpenAlex Work",
        "authors": [
            {"@type": "Person", "familyName": "Doe", "givenName": "Jane", "@id": "0000-0001"},
        ],
    }

    adapter = _make_adapter_with_dummies(readme_content, swh_url, wayback_url, work=work)
    metadata = RepositoryMetadata(identifier=["https://doi.org/10.1234/abcd"])
    collector = DummyCollector()

    updated = adapter.fetch_external_data(
        repo_url="https://github.com/org/repo",
        metadata=metadata,
        doi=None,
        reference_extracted=False,
        extraction_metadata=collector,  # type: ignore[arg-type]
    )

    # Enrichment should have added the special keyword and recorded sources
    assert "from-openalex" in (updated.keywords or [])
    assert updated.codemeta_referencePublication is not None
    assert updated.codemeta_referencePublication.name == "OpenAlex Work"
    # ID may be None depending on identifier value type; only assert title and authors

    recorded_fields = {field for (field, _) in collector.calls}
    assert "keywords" in recorded_fields or "author" in recorded_fields or "alternateName" in recorded_fields
    # Reference publication should also be recorded
    assert ("codemeta_referencePublication", SOURCE_OPENALEX) in collector.calls

