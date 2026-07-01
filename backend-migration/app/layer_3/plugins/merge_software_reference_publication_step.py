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
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin

from app.layer_3.plugins.extract_citation_reference_publication_step import ExtractCitationReferencePublicationStep
from app.layer_3.plugins.extract_openalex_reference_publication_step import ExtractOpenAlexReferencePublicationStep

class MergeSoftwareReferencePublicationStep(ExtractionPlugin):
    """Merge reference-publication candidates from any extraction source."""

    name = "software.merge_reference_publication"
    platforms = {"gitlab", "github"}
    priority_level = 99
    extracts = {"https://discovery.biothings.io/ns/maSMP/referencePublication"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        
        reference = state.data.get("extracted_preferred_reference_publication")
        if reference:
            state.metadata_collector.collect(ExtractCitationReferencePublicationStep.name, "https://discovery.biothings.io/ns/maSMP/referencePublication", reference)
            return state

        openalex_reference = state.data.get("extracted_openalex_reference_publication")
        if openalex_reference:
            state.metadata_collector.collect(ExtractOpenAlexReferencePublicationStep.name, "https://discovery.biothings.io/ns/maSMP/referencePublication", openalex_reference)
            return state

        title = state.data.get("bibtex_title")
        authors = state.data.get("bibtex_authors") or []
        if title or authors:
            codemeta_referencePublication = ReferencePublication(
                type="ScholarlyArticle",
                name=title,
                author=authors if authors else None,
            )
            state.metadata_collector.collect(self.name, "https://discovery.biothings.io/ns/maSMP/referencePublication", codemeta_referencePublication)
        return state


__all__ = ["MergeSoftwareReferencePublicationStep"]
