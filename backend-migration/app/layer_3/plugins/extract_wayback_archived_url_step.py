"""Extract Wayback archivedAt candidates."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState


from app.layer_2.extraction_plugin import ExtractionPlugin

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


class ExtractWaybackArchivedUrlStep(ExtractionPlugin):
    """Extract Wayback candidates for metadata.archivedAt."""

    name = "wayback.extract_archived_url"
    platforms = {"gitlab", "github"}
    extracts = {"https://schema.org/archivedAt"}
    priority_level = 102

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        if "extracted_wayback_archive_url" in state.data:
            return state
        state.data["extracted_wayback_archive_url"] = WaybackClient.check_archive_url(context.repo_url)
        return state



