"""Merge extracted author candidates into software metadata."""

from typing import Any

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.extract_openalex_authors_step import ExtractOpenAlexAuthorsStep
from app.layer_3.plugins.extract_citation_authors_step import ExtractCitationAuthorsStep
from app.layer_2.extraction_plugin import ExtractionPlugin


def _author_key(author: Any) -> tuple[str, str]:
    if isinstance(author, dict):
        family_name = (author.get("familyName") or author.get("family-names") or "") or ""
        given_name = (author.get("givenName") or author.get("given-names") or "") or ""
    else:
        family_name = author.familyName or ""
        given_name = author.givenName or ""
    return family_name.strip(), given_name.strip()


def _author_to_dict(author: Any) -> dict[str, Any]:
    return (
        author.model_dump(by_alias=True, exclude_none=True)
        if not isinstance(author, dict)
        else dict(author)
    )


class MergeSoftwareAuthorsStep(ExtractionPlugin):
    """Merge author candidates from any extraction source."""

    name = "software.extract_authors"
    platforms = {'github', 'gitlab'}
    extracts = {'author'}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:

        # run sub-extractor plugins
        self.plugin_manager.get(ExtractCitationAuthorsStep.name).extract(context, state)
        self.plugin_manager.get(ExtractOpenAlexAuthorsStep.name).extract(context, state)

        citation_authors = state.data.get("extracted_citation_authors") or []
        readme_authors = state.data.get("all_readme_authors") or []
        openalex_authors = state.data.get("extracted_openalex_authors") or []
        candidates = [*citation_authors, *readme_authors, *openalex_authors]

        if not candidates:
            return state

        # merged = list(state.metadata.author or [])
        # seen = {_author_key(author) for author in merged}
        # for author in candidates:
        #     key = _author_key(author)
        #     if key not in seen:
        #         merged.append(_author_to_dict(author))
        #         seen.add(key)
        # state.metadata.author = merged

        if citation_authors:
            state.metadata_collector.collect(ExtractCitationAuthorsStep.name, 'author', citation_authors)
        if readme_authors:
            # state.metadata_collector.collect(ExtractCitationAuthorsStep.name, 'author', citation_authors)
            raise NotImplementedError()
        if openalex_authors:
            state.metadata_collector.collect(ExtractOpenAlexAuthorsStep.name, 'author', citation_authors)
        return state


__all__ = ["MergeSoftwareAuthorsStep"]
