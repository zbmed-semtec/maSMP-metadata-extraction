"""Resolve ``masmp_changeLog`` from prepared changeLog URL candidates."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState

from app.layer_2.extraction_plugin import ExtractionPlugin
from typing import Callable

def first_reachable_url(urls: list[str], is_file_reachable_fn: Callable[[str], bool]) -> str | None:
    for url in urls:
        if is_file_reachable_fn(url):
            return url
    return None

class ExtractMasmpchangeLogLinkStep(ExtractionPlugin):
    """Set ``metadata.masmp_changeLog`` from the first reachable candidate URL."""

    name = "platform.extract_masmp_changeLog_link"
    extracts = {"https://discovery.biothings.io/ns/maSMP/changeLog"}
    platforms = {"github", "gitlab"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        candidates = state.data.get("metadata_file_candidates") or {}
        is_file_reachable_fn = state.data.get("is_file_reachable_fn")
        if not callable(is_file_reachable_fn):
            return state

        changeLog_url = first_reachable_url(candidates.get("changeLog") or [], is_file_reachable_fn)
        if changeLog_url:
            masmp_changeLog =changeLog_url
            state.metadata_collector.collect(self.name, "https://discovery.biothings.io/ns/maSMP/changeLog", masmp_changeLog)

        return state



