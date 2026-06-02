"""Merge extracted citation-entry candidates into software metadata."""

from app.layer_1.provenance.software.defaults import CONFIDENCE_CITATION, SOURCE_CITATION_CFF
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep


class MergeSoftwareCitationEntriesStep(ExtractionStep):
    """Merge citation-entry candidates from any extraction source."""

    name = "software.merge_citation_entries"

    def run(self, context: StepContext, state: StepState) -> StepState:
        entries = [
            state.data.get("extracted_top_level_citation_entry"),
            state.data.get("extracted_preferred_citation_entry"),
        ]
        merged = list(state.metadata.citation or [])
        for entry in entries:
            if entry:
                merged.append(entry)
        if merged:
            state.metadata.citation = merged
            record_field_provenance(state, "citation", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        return state


__all__ = ["MergeSoftwareCitationEntriesStep"]
