"""Merge extracted identifier candidates into software metadata."""
from __future__ import annotations

from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_CITATION,
    CONFIDENCE_README,
    SOURCE_CITATION_CFF,
    SOURCE_README_PARSER,
)
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import StepContext, StepState


class MergeSoftwareIdentifiersStep:
    """Merge identifier candidates from any extraction source."""

    name = "software.merge_identifiers"

    def run(self, context: StepContext, state: StepState) -> StepState:
        citation_identifiers = [
            state.data.get("extracted_top_level_doi_url"),
            state.data.get("extracted_preferred_citation_doi_url"),
        ]
        readme_identifier = state.data.get("extracted_readme_identifier_url")

        identifier_values = list(state.metadata.identifier or [])
        for identifier in [*citation_identifiers, readme_identifier]:
            if identifier and identifier not in identifier_values:
                identifier_values.append(identifier)
        if not identifier_values:
            return state

        state.metadata.identifier = identifier_values
        if any(citation_identifiers):
            record_field_provenance(state, "identifier", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        if readme_identifier:
            record_field_provenance(state, "identifier", SOURCE_README_PARSER, CONFIDENCE_README)
        return state


__all__ = ["MergeSoftwareIdentifiersStep"]
