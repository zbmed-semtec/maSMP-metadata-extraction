"""Extract author candidates from OpenAlex."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.external.openalex.helpers import OpenAlexClient
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.authors_from_work import (
    authors_from_openalex_work,
)
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.work_lookup import (
    get_openalex_work,
)


class ExtractOpenAlexAuthorsStep(ExtractionStep):
    """Extract OpenAlex author candidates for metadata.author."""

    name = "openalex.extract_authors"

    def __init__(self, client: OpenAlexClient | None = None) -> None:
        super().__init__()
        self.client = client or OpenAlexClient()

    def run(self, context: StepContext, state: StepState) -> StepState:
        _, work_data = get_openalex_work(state, self.client)
        if work_data:
            state.data["extracted_openalex_authors"] = authors_from_openalex_work(work_data)
        return state


__all__ = ["ExtractOpenAlexAuthorsStep"]
