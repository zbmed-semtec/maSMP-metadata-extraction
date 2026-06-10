"""Wayback archive lookup helper."""

import requests


def lookup_wayback(repo_url: str, timeout: int = 5) -> str | None:
    """Return Wayback archive URL when reachable."""
    archive_url = f"https://web.archive.org/web/{repo_url}"
    try:
        response = requests.get(archive_url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return archive_url
    except requests.exceptions.RequestException:
        return None
    return None


class WaybackClient:
    """HTTP check for web.archive.org mirror of a repo URL."""

    @staticmethod
    def check_archive_url(url: str, timeout: int = 5) -> str | None:
        return lookup_wayback(url, timeout=timeout)


__all__ = ["WaybackClient", "lookup_wayback"]
