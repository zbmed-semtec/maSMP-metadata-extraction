"""
Unit tests for WaybackClient.
Cover successful and failing archive lookups for both Wayback and Software Heritage.
"""
from app.domain.services.wayback_client import WaybackClient


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


def test_check_software_heritage_success(monkeypatch):
    client = WaybackClient()

    def fake_get(url: str, timeout: int = 5, allow_redirects: bool = True):
        assert url.startswith("https://archive.softwareheritage.org/browse/origin/directory/")
        return DummyResponse(200)

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    result = client.check_software_heritage("https://example.com/repo")
    assert result == "https://archive.softwareheritage.org/browse/origin/directory/?origin_url=https://example.com/repo"


def test_find_archive_prefers_software_heritage(monkeypatch):
    client = WaybackClient()

    def fake_check_swh(url: str, timeout: int = 5):
        return "swh-url"

    def fake_check_wayback(url: str, timeout: int = 5):
        return "wayback-url"

    monkeypatch.setattr(WaybackClient, "check_software_heritage", staticmethod(fake_check_swh))
    monkeypatch.setattr(WaybackClient, "check_archive_url", staticmethod(fake_check_wayback))

    result = client.find_archive("https://example.com/repo")
    assert result == "swh-url"

