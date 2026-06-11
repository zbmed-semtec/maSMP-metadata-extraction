"""Extract alternate-name candidates from OpenAlex."""
from __future__ import annotations

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.openalex.helpers import OpenAlexClient
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.work_lookup import (
    get_openalex_work,
)


class ExtractOpenAlexAlternateNamesStep:
    """Extract OpenAlex title candidates for metadata.alternateName."""

    name = "openalex.extract_alternate_names"

    def __init__(self, client: OpenAlexClient | None = None) -> None:
        self.client = client or OpenAlexClient()

    def run(self, context: StepContext, state: StepState) -> StepState:
        _, work_data = get_openalex_work(state, self.client)
        if work_data and work_data.get("title"):
            state.data["extracted_openalex_title"] = str(work_data["title"])
        return state


__all__ = ["ExtractOpenAlexAlternateNamesStep"]

