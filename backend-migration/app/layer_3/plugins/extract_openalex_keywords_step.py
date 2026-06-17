"""Extract keyword candidates from OpenAlex."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.plugins.openalex_client_plugin import OpenAlexClient
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.work_lookup import (
    get_openalex_work,
)


def _keywords_from_openalex_work(work_data: dict) -> list[str]:
    """Read OpenAlex keyword display names from a work payload."""
    keywords: list[str] = []
    for keyword in work_data.get("keywords", []) or []:
        if isinstance(keyword, dict) and keyword.get("display_name"):
            keywords.append(keyword["display_name"])
        elif isinstance(keyword, str) and keyword:
            keywords.append(keyword)
    return keywords


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractOpenAlexKeywordsStep(ExtractionPlugin):
    """Extract OpenAlex keyword candidates for metadata.keywords."""

    name = "openalex.extract_keywords"
    client : OpenAlexClient
    platforms = {"github", "gitlab"}
    extracts = {"keywords"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        self.client = self.plugin_manager.get("openalex_client_plugin")
        _, work_data = get_openalex_work(state, self.client)
        if not work_data:
            return state
        state.data["extracted_openalex_keywords"] = _keywords_from_openalex_work(work_data)
        return state


__all__ = ["ExtractOpenAlexKeywordsStep"]
