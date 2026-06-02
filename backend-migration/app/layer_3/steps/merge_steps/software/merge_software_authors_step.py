"""Merge extracted author candidates into software metadata."""

from typing import Any

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
from app.layer_3.steps.contracts.step import ExtractionStep


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


class MergeSoftwareAuthorsStep(ExtractionStep):
    """Merge author candidates from any extraction source."""

    name = "software.merge_authors"

    def run(self, context: StepContext, state: StepState) -> StepState:
        citation_authors = state.data.get("extracted_citation_authors") or []
        readme_authors = state.data.get("all_readme_authors") or []
        openalex_authors = state.data.get("extracted_openalex_authors") or []
        candidates = [*citation_authors, *readme_authors, *openalex_authors]

        if not candidates:
            return state

        merged = list(state.metadata.author or [])
        seen = {_author_key(author) for author in merged}
        for author in candidates:
            key = _author_key(author)
            if key not in seen:
                merged.append(_author_to_dict(author))
                seen.add(key)
        state.metadata.author = merged

        if citation_authors:
            record_field_provenance(state, "author", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        if readme_authors:
            record_field_provenance(state, "author", SOURCE_README_PARSER, CONFIDENCE_README)
        if openalex_authors:
            record_field_provenance(state, "author", SOURCE_OPENALEX, CONFIDENCE_OPENALEX)
        return state


__all__ = ["MergeSoftwareAuthorsStep"]
