"""Shared OpenAlex work fetch + cache (used by all OpenAlex property extract steps)."""
from __future__ import annotations

from typing import Optional

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import StepState
from app.layer_3.steps.extract_steps.services.external.openalex.helpers.openalex_client import OpenAlexClient


def get_openalex_work(state: StepState, client: OpenAlexClient) -> tuple[Optional[str], Optional[dict]]:
    """Fetch and cache the OpenAlex work payload for the current DOI."""
    effective_doi = _resolve_effective_doi(state.metadata, state.data.get("doi"))
    if not effective_doi:
        state.data["extracted_openalex_work"] = None
        return None, None

    if "extracted_openalex_work" not in state.data:
        state.data["extracted_openalex_work"] = client.fetch_work_by_doi(effective_doi)
    return effective_doi, state.data.get("extracted_openalex_work")


def _resolve_effective_doi(metadata: SoftwareMetadata, doi: Optional[str]) -> Optional[str]:
    if doi:
        return doi.replace("https://doi.org/", "")
    id_value = metadata.identifier
    candidate = None
    if isinstance(id_value, list):
        candidate = next((v for v in id_value if isinstance(v, str) and "doi.org" in v), None)
    elif isinstance(id_value, str) and "doi.org" in id_value:
        candidate = id_value
    return candidate.replace("https://doi.org/", "") if candidate else None


__all__ = ["get_openalex_work"]
