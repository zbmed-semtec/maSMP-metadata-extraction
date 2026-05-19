"""Extract authors from CITATION.cff into step state."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded


class ExtractCitationAuthorsStep:
    """Extract top-level CFF authors without mutating metadata."""

    name = "citation.extract_authors"

    def run(self, context: StepContext, state: StepState) -> StepState:
        ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        extracted_authors = []
        for author in state.data["cff_data"].get("authors") or []:
            person = {
                "@type": "Person",
                "familyName": author.get("family-names"),
                "givenName": author.get("given-names"),
            }
            if "orcid" in author:
                person["@id"] = author["orcid"]
            extracted_authors.append(person)
        state.data["extracted_citation_authors"] = extracted_authors
        return state


__all__ = ["ExtractCitationAuthorsStep"]

