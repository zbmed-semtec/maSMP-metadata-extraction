"""Extract reference-publication candidates from OpenAlex."""

from app.layer_1.entities.shared_primitives import Person, ReferencePublication
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.authors_from_work import (
    authors_from_openalex_work,
)
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.work_lookup import (
    get_openalex_work,
)


from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.openalex_client_plugin import OpenAlexClient


class ExtractOpenAlexReferencePublicationStep(ExtractionPlugin):
    """Extract OpenAlex candidates for metadata.codemeta_referencePublication."""

    name = "openalex.extract_reference_publication"
    client : OpenAlexClient
    platforms = {"github", "gitlab"}
    extracts = {"citation"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        self.client = self.plugin_manager.get("openalex_client_plugin")
        if state.data.get("reference_extracted"):
            return state
        effective_doi, work_data = get_openalex_work(state, self.client)
        if not effective_doi or not work_data:
            return state
        authors = state.data.get("extracted_openalex_authors")
        if authors is None:
            authors = authors_from_openalex_work(work_data)
        state.data["extracted_openalex_reference_publication"] = _build_reference_publication(
            effective_doi=effective_doi,
            work_data=work_data,
            authors=authors,
        )
        return state


def _build_reference_publication(
    *,
    effective_doi: str,
    work_data: dict,
    authors: list[dict],
) -> ReferencePublication:
    return ReferencePublication(
        type="ScholarlyArticle",
        id=f"https://doi.org/{effective_doi}",
        name=work_data.get("title"),
        author=[
            Person(
                type=author.get("@type", "Person"),
                familyName=author.get("familyName"),
                givenName=author.get("givenName"),
                id=author.get("@id"),
            )
            for author in authors
        ]
        or None,
    )


__all__ = ["ExtractOpenAlexReferencePublicationStep"]

