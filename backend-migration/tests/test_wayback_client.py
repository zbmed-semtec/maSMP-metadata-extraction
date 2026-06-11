"""
Unit tests for WaybackClient (web.archive.org lookups only).
"""
from __future__ import annotations
from app.layer_3.steps.extract_steps.services.external.wayback.helpers.extract_archive import WaybackClient


class DummyResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception("HTTP error")


def test_check_archive_url_success(monkeypatch):
    client = WaybackClient()

    def fake_get(url: str, timeout: int = 5, allow_redirects: bool = True):
        assert url.startswith("https://web.archive.org/web/")
        return DummyResponse(200)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    result = client.check_archive_url("https://example.com")
    assert result == "https://web.archive.org/web/https://example.com"


def test_check_archive_url_not_found(monkeypatch):
    client = WaybackClient()

    def fake_get(url: str, timeout: int = 5, allow_redirects: bool = True):
        return DummyResponse(404)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)
    assert client.check_archive_url("https://example.com") is None
