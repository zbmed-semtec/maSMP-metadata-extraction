"""Merge extracted keyword candidates into software metadata."""

from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_CITATION,
    CONFIDENCE_OPENALEX,
    CONFIDENCE_PLATFORM,
    SOURCE_CITATION_CFF,
    SOURCE_OPENALEX,
)
from app.layer_3.extraction_metadata.record import platform_source_for, record_field_provenance
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin


class MergeSoftwareKeywordsStep(ExtractionPlugin):
    """Merge keyword candidates from any extraction source."""

    name = "software.merge_keywords"
    platforms = {"gitlab", "github"}
    extracts = {"keywords"}
    priority_level = 99

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
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
        elif citation_keywords:
            record_field_provenance(state, "keywords", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        elif openalex_keywords:
            record_field_provenance(state, "keywords", SOURCE_OPENALEX, CONFIDENCE_OPENALEX)
        return state


__all__ = ["MergeSoftwareKeywordsStep"]
