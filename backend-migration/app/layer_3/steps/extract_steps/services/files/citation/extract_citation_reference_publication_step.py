"""Extract preferred CITATION.cff reference publication into step state."""

from typing import Any, Dict, List

from app.layer_1.entities.shared_primitives import Person, ReferencePublication
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded


class ExtractCitationReferencePublicationStep(ExtractionStep):
    """Build preferred citation values without mutating metadata."""

    name = "citation.extract_reference_publication"

    def run(self, context: StepContext, state: StepState) -> StepState:
        ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            state.data["reference_extracted"] = False
            return state
        preferred = state.data.get("preferred") or {}
        state.data["reference_extracted"] = False
        state.data["extracted_preferred_reference_publication"] = None
        state.data["extracted_preferred_citation_entry"] = None
        if preferred:
            state.data["reference_extracted"] = True
            authors: List[Person] = []
            for author in preferred.get("authors") or []:
                author_obj = Person(
                    type="Person",
                    familyName=author.get("family-names"),
                    givenName=author.get("given-names"),
                )
                if "orcid" in author:
                    author_obj.id = author["orcid"]
                authors.append(author_obj)

            reference_publication = ReferencePublication(
                type="ScholarlyArticle",
                id=f"https://doi.org/{preferred['doi']}" if preferred.get("doi") else None,
                name=preferred.get("title"),
                author=authors if authors else None,
            )
            state.data["extracted_preferred_reference_publication"] = reference_publication
            doi_value = preferred.get("doi")
            if doi_value:
                doi_url = f"https://doi.org/{doi_value}"
                citation_entry: Dict[str, Any] = {"@type": "Article", "@id": doi_url}
                title = preferred.get("title")
                if title:
                    citation_entry["title"] = str(title)
                authors = reference_publication.author or []
                if authors:
                    citation_authors: List[Dict[str, Any]] = []
                    for author in authors:
                        person: Dict[str, Any] = {"@type": "Person"}
                        if author.givenName:
                            person["givenName"] = author.givenName
                        if author.familyName:
                            person["familyName"] = author.familyName
                        if author.id:
                            person["@id"] = author.id
                        citation_authors.append(person)
                    if citation_authors:
                        citation_entry["author"] = citation_authors
                state.data["extracted_preferred_citation_entry"] = citation_entry
        return state


__all__ = ["ExtractCitationReferencePublicationStep"]

