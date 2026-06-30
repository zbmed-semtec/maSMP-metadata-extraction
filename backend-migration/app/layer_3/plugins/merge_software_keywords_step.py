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
from app.layer_3.plugins.extract_citation_keywords_step import ExtractCitationKeywordsStep
from app.layer_3.plugins.extract_openalex_keywords_step import ExtractOpenAlexKeywordsStep
from app.layer_3.plugins.gitlab.extract_gitlab_keywords_step import ExtractGitlabKeywordsStep

class MergeSoftwareKeywordsStep(ExtractionPlugin):
    """Merge keyword candidates from any extraction source."""

    name = "software.merge_keywords"
    platforms = {"gitlab", "github"}
    extracts = {"keywords"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:

        platform_keywords = state.data.get("extracted_platform_keywords") or []
        citation_keywords = state.data.get("extracted_keywords") or []
        openalex_keywords = state.data.get("extracted_openalex_keywords") or []

        keywords = [*platform_keywords, *citation_keywords, *openalex_keywords]
        if not keywords:
            return state

        # state.metadata_collector.collect(ExtractCitationKeywordsStep.name, 'keywords', citation_keywords)
        # state.metadata_collector.collect(ExtractOpenAlexKeywordsStep.name, 'keywords', openalex_keywords)
        # state.metadata_collector.collect(ExtractGitlabKeywordsStep.name, 'keywords', platform_keywords)

        state.metadata_collector.collect(self.name, 'keywords', keywords)

        return state


__all__ = ["MergeSoftwareKeywordsStep"]
