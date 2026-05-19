"""Tests for Software Heritage origin URL lookup."""

from app.layer_3.steps.extract_steps.services.external.software_heritage.helpers.extract_archive import (
    lookup_software_heritage,
)


class DummyResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception("HTTP error")


def test_lookup_software_heritage_success(monkeypatch):
    def fake_get(url: str, timeout: int = 5, allow_redirects: bool = True):
        assert url.startswith("https://archive.softwareheritage.org/browse/origin/directory/")
        return DummyResponse(200)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    result = lookup_software_heritage("https://example.com/repo")
    assert result == "https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://example.com/repo"
