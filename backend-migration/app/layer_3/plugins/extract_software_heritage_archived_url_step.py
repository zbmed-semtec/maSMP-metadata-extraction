"""Extract Software Heritage archivedAt candidates."""

from collections.abc import Callable

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState


from app.layer_2.extraction_plugin import ExtractionPlugin

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

class ExtractSoftwareHeritageArchivedUrlStep(ExtractionPlugin):
    """Extract Software Heritage candidates for metadata.archivedAt."""

    name = "software_heritage.extract_archived_url"
    platforms = {"gitlab", "github"}
    extracts = {"https://schema.org/archivedAt"}
    priority_level = 102


    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        self._lookup_fn = lookup_software_heritage
        if "extracted_software_heritage_archive_url" in state.data:
            return state
        state.data["extracted_software_heritage_archive_url"] = self._lookup_fn(context.repo_url)
        return state



