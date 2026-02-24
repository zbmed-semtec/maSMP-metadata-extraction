"""
Unit tests for OpenAlexClient.
Cover DOI cleaning, fetch_work_by_doi error handling, author and keyword extraction,
and metadata enrichment including merge semantics.
"""
from typing import Any, Dict

import pytest

from app.domain.services.openalex_client import OpenAlexClient
from app.core.entities.repository_metadata import RepositoryMetadata


class DummyResponse:
    def __init__(self, status_code: int, json_data: Dict[str, Any] | None = None):
        self.status_code = status_code
        self._json = json_data or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception("HTTP error")

    def json(self) -> Dict[str, Any]:
        return self._json


def test_fetch_work_by_doi_cleans_prefix_and_handles_errors(monkeypatch):
    client = OpenAlexClient()

    calls: list[str] = []

    def fake_get(url: str, timeout: int = 10):
        calls.append(url)
        # Simulate success
        return DummyResponse(200, {"id": "W/123"})

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    data = client.fetch_work_by_doi("https://doi.org/10.1234/xyz")
    assert data == {"id": "W/123"}
    assert calls[0].endswith("/doi:10.1234/xyz")


def test_fetch_work_by_doi_returns_none_on_exception(monkeypatch):
    client = OpenAlexClient()

    def fake_get(url: str, timeout: int = 10):
        import requests
        raise requests.exceptions.RequestException("network error")

    import requests

    monkeypatch.setattr(requests, "get", fake_get)
    assert client.fetch_work_by_doi("10.1/err") is None


def test_extract_authors_and_keywords():
    client = OpenAlexClient()
    work = {
        "authorships": [
            {"author": {"display_name": "Jane Doe", "orcid": "0000-0001"}},
            {"author": {"display_name": "SingleName"}},
        ],
        "keywords": [
            {"display_name": "metadata"},
            {"display_name": "software"},
        ],
    }

    authors = client.extract_authors(work)
    assert len(authors) == 2
    assert authors[0]["familyName"] == "Doe"
    assert authors[0]["givenName"] == "Jane"
    assert authors[0]["@id"] == "0000-0001"

    keywords = client.extract_keywords(work)
    assert set(keywords) == {"metadata", "software"}


def test_enrich_metadata_uses_identifier_when_doi_not_passed(monkeypatch):
    client = OpenAlexClient()

    work = {
        "title": "OpenAlex Title",
        "authorships": [
            {"author": {"display_name": "Jane Doe"}},
        ],
        "keywords": [{"display_name": "openalex"}],
    }

    def fake_fetch(doi: str):
        # Should receive cleaned bare DOI from identifier list
        assert doi == "10.1234/abcd"
        return work

    monkeypatch.setattr(client, "fetch_work_by_doi", fake_fetch)

    metadata = RepositoryMetadata(
        identifier=["https://doi.org/10.1234/abcd"],
        alternateName=["Existing"],
        keywords=["existing"],
        author=[{"familyName": "Doe", "givenName": "Jane"}],
    )

    enriched = client.enrich_metadata(metadata, doi=None)

    # alternateName merged
    assert set(enriched.alternateName or []) == {"Existing", "OpenAlex Title"}
    # keywords merged
    assert "openalex" in (enriched.keywords or [])
    assert "existing" in (enriched.keywords or [])
    # authors merged/deduped
    assert enriched.author is not None
    # The existing author should still be present (possibly with @id added)
    found = False
    for a in enriched.author:
        if a.get("familyName") == "Doe" and a.get("givenName") == "Jane":
            found = True
            break
    assert found

