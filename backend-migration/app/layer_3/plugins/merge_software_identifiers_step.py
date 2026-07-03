"""Merge extracted identifier candidates into software metadata."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.extract_citation_doi_step import ExtractCitationDoiStep
from app.layer_3.plugins.extract_readme_identifier_step import ExtractReadmeIdentifierStep


class MergeSoftwareIdentifiersStep(ExtractionPlugin):
    """Merge identifier candidates from any extraction source."""

    name = "software.merge_identifiers"
    platforms = {"gitlab", "github"}
    extracts = {"https://schema.org/identifier"}
    priority_level = 98

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        citation_identifiers = [
            state.data.get("extracted_top_level_doi_url"),
            state.data.get("extracted_preferred_citation_doi_url"),
        ]

        readme_identifier = state.data.get("extracted_readme_identifier_url")

        for citation in citation_identifiers:
            if citation:
                state.metadata_collector.collect(ExtractCitationDoiStep.name, "https://schema.org/identifier", citation)
        if readme_identifier:
            state.metadata_collector.collect(ExtractReadmeIdentifierStep.name, "https://schema.org/identifier", readme_identifier)
        return state


__all__ = ["MergeSoftwareIdentifiersStep"]
