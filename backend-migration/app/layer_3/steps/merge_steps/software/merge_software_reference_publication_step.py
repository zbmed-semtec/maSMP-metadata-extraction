"""Merge extracted reference-publication candidates into software metadata."""

from app.layer_1.entities.shared_primitives import ReferencePublication
from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_CITATION,
    CONFIDENCE_OPENALEX,
    CONFIDENCE_README,
    SOURCE_CITATION_CFF,
    SOURCE_OPENALEX,
    SOURCE_README_PARSER,
)
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import StepContext, StepState


class MergeSoftwareReferencePublicationStep:
    """Merge reference-publication candidates from any extraction source."""

    name = "software.merge_reference_publication"

    def run(self, context: StepContext, state: StepState) -> StepState:
        reference = state.data.get("extracted_preferred_reference_publication")
        if reference:
            state.metadata.codemeta_referencePublication = reference
            record_field_provenance(
                state,
                "codemeta_referencePublication",
                SOURCE_CITATION_CFF,
                CONFIDENCE_CITATION,
            )
            return state

        openalex_reference = state.data.get("extracted_openalex_reference_publication")
        if openalex_reference and not state.metadata.codemeta_referencePublication:
            state.metadata.codemeta_referencePublication = openalex_reference
            record_field_provenance(
                state,
                "codemeta_referencePublication",
                SOURCE_OPENALEX,
                CONFIDENCE_OPENALEX,
            )
            return state

        if state.metadata.codemeta_referencePublication:
            return state

        title = state.data.get("bibtex_title")
        authors = state.data.get("bibtex_authors") or []
        if title or authors:
            state.metadata.codemeta_referencePublication = ReferencePublication(
                type="ScholarlyArticle",
                name=title,
                author=authors if authors else None,
            )
            record_field_provenance(
                state,
                "codemeta_referencePublication",
                SOURCE_README_PARSER,
                CONFIDENCE_README,
            )
        return state


__all__ = ["MergeSoftwareReferencePublicationStep"]
