"""Extract title from CITATION.cff into step state."""
from __future__ import annotations

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded


class ExtractCitationTitleStep:
    """Extract CFF title without mutating metadata."""

    name = "citation.extract_title"

    def run(self, context: StepContext, state: StepState) -> StepState:
        ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        title = state.data["cff_data"].get("title")
        state.data["extracted_title"] = str(title) if title else None
        return state


__all__ = ["ExtractCitationTitleStep"]

