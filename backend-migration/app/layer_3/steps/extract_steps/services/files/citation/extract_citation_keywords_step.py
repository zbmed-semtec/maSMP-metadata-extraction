"""Extract keywords from CITATION.cff into step state."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded


class ExtractCitationKeywordsStep(ExtractionStep):
    """Extract CFF keywords without mutating metadata."""

    name = "citation.extract_keywords"

    def run(self, context: StepContext, state: StepState) -> StepState:
        ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        keywords = state.data["cff_data"].get("keywords")
        state.data["extracted_keywords"] = list(keywords) if isinstance(keywords, list) else []
        return state


__all__ = ["ExtractCitationKeywordsStep"]

