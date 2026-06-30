"""Merge extracted alternate-name candidates into software metadata."""

from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_CITATION,
    CONFIDENCE_OPENALEX,
    SOURCE_CITATION_CFF,
    SOURCE_OPENALEX,
)
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin


class MergeSoftwareAlternateNamesStep(ExtractionPlugin):
    """Merge alternate-name candidates from any extraction source."""

    name = "software.merge_alternate_names"
    platforms = {"gitlab", "github"}
    extracts = {"alternateName"}
    priority_level = 99

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        citation_title = state.data.get("extracted_title")
        openalex_title = state.data.get("extracted_openalex_title")

        existing = list(state.metadata.alternateName or [])
        for title in (citation_title, openalex_title):
            if title and title not in existing:
                existing.append(title)
        if not existing:
            return state

        state.metadata.alternateName = existing
        if citation_title:
            record_field_provenance(state, "alternateName", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        if openalex_title:
            record_field_provenance(state, "alternateName", SOURCE_OPENALEX, CONFIDENCE_OPENALEX)
        return state


__all__ = ["MergeSoftwareAlternateNamesStep"]
