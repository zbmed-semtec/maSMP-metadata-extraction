"""Resolve ``codemeta_readme`` from prepared README URL candidates."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin
from typing import Callable

from app.layer_2.extraction_plugin import ExtractionPlugin

def first_reachable_url(urls: list[str], is_file_reachable_fn: Callable[[str], bool]) -> str | None:
    for url in urls:
        if is_file_reachable_fn(url):
            return url
    return None

class ExtractCodemetaReadmeLinkStep(ExtractionPlugin):
    """Set ``metadata.codemeta_readme`` from the first reachable candidate URL."""

    name = "platform.extract_codemeta_readme_link"
    extracts = {"readme"}
    platforms = {"gitlab", "github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        candidates = state.data.get("metadata_file_candidates") or {}
        is_file_reachable_fn = state.data.get("is_file_reachable_fn")
        if not callable(is_file_reachable_fn):
            return state
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        readme_url = first_reachable_url(candidates.get("readme") or [], is_file_reachable_fn)
        if readme_url:
            codemeta_readme =readme_url
            state.metadata_collector.collect(self.name, "readme", codemeta_readme)

        return state



