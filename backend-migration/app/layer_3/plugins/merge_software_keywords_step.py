"""Merge extracted keyword candidates into software metadata."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.extract_citation_keywords_step import ExtractCitationKeywordsStep
from app.layer_3.plugins.extract_openalex_keywords_step import ExtractOpenAlexKeywordsStep
from app.layer_3.plugins.gitlab.extract_gitlab_keywords_step import ExtractGitlabKeywordsStep

class MergeSoftwareKeywordsStep(ExtractionPlugin):
    """Merge keyword candidates from any extraction source."""

    name = "software.merge_keywords"
    platforms = {"gitlab", "github"}
    extracts = {"https://schema.org/keywords"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:

        platform_keywords = state.data.get("extracted_platform_keywords") or []
        citation_keywords = state.data.get("extracted_keywords") or []
        openalex_keywords = state.data.get("extracted_openalex_keywords") or []

        keywords = [*platform_keywords, *citation_keywords, *openalex_keywords]
        if not keywords:
            return state

        # state.metadata_collector.collect(ExtractCitationKeywordsStep.name, "https://schema.org/keywords", citation_keywords)
        # state.metadata_collector.collect(ExtractOpenAlexKeywordsStep.name, "https://schema.org/keywords", openalex_keywords)
        # state.metadata_collector.collect(ExtractGitlabKeywordsStep.name, "https://schema.org/keywords", platform_keywords)

        state.metadata_collector.collect(self.name, "https://schema.org/keywords", keywords)

        return state


__all__ = ["MergeSoftwareKeywordsStep"]
