"""Resolve ``masmp_changelog`` from prepared CHANGELOG URL candidates."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState

from app.layer_2.extraction_plugin import ExtractionPlugin
from typing import Callable

def first_reachable_url(urls: list[str], is_file_reachable_fn: Callable[[str], bool]) -> str | None:
    for url in urls:
        if is_file_reachable_fn(url):
            return url
    return None

class ExtractMasmpChangelogLinkStep(ExtractionPlugin):
    """Set ``metadata.masmp_changelog`` from the first reachable candidate URL."""

    name = "platform.extract_masmp_changelog_link"
    extracts = {"maSMP:changelog"}
    platforms = {"github", "gitlab"}


    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        candidates = state.data.get("metadata_file_candidates") or {}
        is_file_reachable_fn = state.data.get("is_file_reachable_fn")
        if not callable(is_file_reachable_fn):
            return state

        changelog_url = first_reachable_url(candidates.get("changelog") or [], is_file_reachable_fn)
        if changelog_url:
            masmp_changelog =changelog_url
            state.metadata_collector.collect(self.name, "masmp_changelog", masmp_changelog)

        return state



