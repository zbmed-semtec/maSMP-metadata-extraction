"""
Unit tests for OpenAlexClient (HTTP only) and shared author parsing helper.
"""
from __future__ import annotations
from typing import Any, Dict

from app.layer_3.steps.extract_steps.services.external.openalex.extract_openalex_keywords_step import (
    _keywords_from_openalex_work,
)
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.authors_from_work import (
    authors_from_openalex_work,
)
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.openalex_client import OpenAlexClient


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


def test_authors_from_openalex_work():
    work = {
        "authorships": [
            {"author": {"display_name": "Jane Doe", "orcid": "0000-0001"}},
            {"author": {"display_name": "SingleName"}},
        ],
    }
    authors = authors_from_openalex_work(work)
    assert len(authors) == 2
    assert authors[0]["familyName"] == "Doe"
    assert authors[0]["givenName"] == "Jane"
    assert authors[0]["@id"] == "0000-0001"


def test_keywords_from_openalex_work_display_name_and_plain_strings():
    work = {
        "keywords": [
            {"display_name": "metadata"},
            {"display_name": "software"},
            "plain-tag",
        ],
    }
    assert set(_keywords_from_openalex_work(work)) == {"metadata", "software", "plain-tag"}
