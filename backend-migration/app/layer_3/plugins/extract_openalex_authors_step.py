"""Extract author candidates from OpenAlex."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.openalex.helpers import OpenAlexClient
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.authors_from_work import (
    authors_from_openalex_work,
)
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.work_lookup import (
    get_openalex_work,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractOpenAlexAuthorsStep(ExtractionPlugin):
    """Extract OpenAlex author candidates for metadata.author."""

    name = "openalex.extract_authors"
    extracts = {"author"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        self.client = self.plugin_manager.get("openalex_client_plugin")
        _, work_data = get_openalex_work(state, self.client)
        if work_data:
            state.data["extracted_openalex_authors"] = authors_from_openalex_work(work_data)
        return state


__all__ = ["ExtractOpenAlexAuthorsStep"]
