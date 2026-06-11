"""Software Heritage archive lookup helper."""
from __future__ import annotations

import requests


def lookup_software_heritage(repo_url: str, timeout: int = 5) -> str | None:
    """Return Software Heritage archive URL when reachable."""
    archive_url = f"https://archive.softwareheritage.org/browse/origin/directory/?origin_url={repo_url}"
    try:
        response = requests.get(archive_url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return archive_url
    except requests.exceptions.RequestException:
        return None
    return None
