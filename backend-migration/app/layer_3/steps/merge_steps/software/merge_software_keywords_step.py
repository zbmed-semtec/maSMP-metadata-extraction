"""Merge extracted keyword candidates into software metadata."""

from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_CITATION,
    CONFIDENCE_OPENALEX,
    CONFIDENCE_PLATFORM,
    SOURCE_CITATION_CFF,
    SOURCE_OPENALEX,
)
from app.layer_3.extraction_metadata.record import platform_source_for, record_field_provenance
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep


class MergeSoftwareKeywordsStep(ExtractionStep):
    """Merge keyword candidates from any extraction source."""

    name = "software.merge_keywords"

    def run(self, context: StepContext, state: StepState) -> StepState:
        platform_keywords = state.data.get("extracted_platform_keywords") or []
        citation_keywords = state.data.get("extracted_keywords") or []
        openalex_keywords = state.data.get("extracted_openalex_keywords") or []

        keywords = [*platform_keywords, *citation_keywords, *openalex_keywords]
        if not keywords:
            return state

        existing = state.metadata.keywords or []
        state.metadata.keywords = list(set(existing) | set(keywords))

        if platform_keywords:
            record_field_provenance(
                state,
                "keywords",
                platform_source_for(context),
                CONFIDENCE_PLATFORM,
            )
        if citation_keywords:
            record_field_provenance(state, "keywords", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        if openalex_keywords:
            record_field_provenance(state, "keywords", SOURCE_OPENALEX, CONFIDENCE_OPENALEX)
        return state


__all__ = ["MergeSoftwareKeywordsStep"]
