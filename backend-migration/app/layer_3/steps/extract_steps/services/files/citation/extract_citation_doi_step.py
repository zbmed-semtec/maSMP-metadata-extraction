"""Extract DOI and citation entries from CITATION.cff into step state."""

from typing import Any, Dict, List

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded


class ExtractCitationDoiStep(ExtractionStep):
    """Extract DOI values and citation entries without mutating metadata."""

    name = "citation.extract_doi"

    def run(self, context: StepContext, state: StepState) -> StepState:
        ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        cff_data = state.data["cff_data"]
        doi = None
        state.data["extracted_top_level_citation_entry"] = None
        state.data["extracted_preferred_citation_doi_url"] = None
        state.data["extracted_top_level_doi_url"] = None
        if cff_data.get("doi"):
            doi = str(cff_data["doi"])
            doi_url = f"https://doi.org/{doi}"
            state.data["extracted_top_level_doi_url"] = doi_url
            citation_entry: Dict[str, Any] = {"@type": "Article", "@id": doi_url}
            title = cff_data.get("title")
            if title:
                citation_entry["title"] = str(title)
            authors_field = cff_data.get("authors") or []
            author_list: List[Dict[str, Any]] = []
            for author in authors_field:
                if not isinstance(author, dict):
                    continue
                given = author.get("given-names")
                family = author.get("family-names")
                if not given and not family and not author.get("orcid"):
                    continue
                person: Dict[str, Any] = {"@type": "Person"}
                if given:
                    person["givenName"] = given
                if family:
                    person["familyName"] = family
                if author.get("orcid"):
                    person["@id"] = author["orcid"]
                author_list.append(person)
            if author_list:
                citation_entry["author"] = author_list
            state.data["extracted_top_level_citation_entry"] = citation_entry
        preferred = cff_data.get("preferred-citation") or {}
        preferred_doi = preferred.get("doi")
        if preferred_doi:
            state.data["extracted_preferred_citation_doi_url"] = (
                f"https://doi.org/{str(preferred_doi)}"
            )
        state.data["doi"] = doi
        state.data["preferred"] = preferred
        return state


__all__ = ["ExtractCitationDoiStep"]

