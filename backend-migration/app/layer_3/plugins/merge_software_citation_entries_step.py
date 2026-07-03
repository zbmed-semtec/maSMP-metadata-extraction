"""Merge extracted citation-entry candidates into software metadata."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.extract_citation_doi_step import ExtractCitationDoiStep
from app.layer_3.plugins.extract_citation_reference_publication_step import ExtractCitationReferencePublicationStep

class MergeSoftwareCitationEntriesStep(ExtractionPlugin):
    """Merge citation-entry candidates from any extraction source."""

    name = "software.merge_citation_entries"
    platforms = {"gitlab", "github"}
    extracts = {"https://schema.org/citation"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        self.plugin_manager.get(ExtractCitationDoiStep.name).extract(context, state)
        self.plugin_manager.get(ExtractCitationReferencePublicationStep.name).extract(context, state)
        
        entries = [
            state.data.get("extracted_top_level_citation_entry"),
            state.data.get("extracted_preferred_citation_entry"),
        ]


        merged = []
        for entry in entries:
            if entry:
                merged.append(entry)

        if len(merged) > 0:
            state.metadata_collector.collect(self.name, "https://schema.org/citation", merged)

        return state


__all__ = ["MergeSoftwareCitationEntriesStep"]
