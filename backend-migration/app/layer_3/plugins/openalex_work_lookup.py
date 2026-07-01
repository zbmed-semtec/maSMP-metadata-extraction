"""Shared OpenAlex work fetch + cache (used by all OpenAlex property extract steps)."""

from typing import Optional

from app.layer_1.metadata_collector.metadata_collector import MetadataCollector
from app.layer_3.steps.contracts import ExtractionState
from app.layer_3.plugins.openalex_client_plugin import OpenAlexClient

def get_openalex_work(state: ExtractionState, client: OpenAlexClient) -> tuple[Optional[str], Optional[dict]]:
    """Fetch and cache the OpenAlex work payload for the current DOI."""
    effective_doi = _resolve_effective_doi(state.metadata_collector, state.data.get("doi"))
    if not effective_doi:
        state.data["extracted_openalex_work"] = None
        return None, None

    if "extracted_openalex_work" not in state.data:
        state.data["extracted_openalex_work"] = client.fetch_work_by_doi(effective_doi)
    return effective_doi, state.data.get("extracted_openalex_work")


def _resolve_effective_doi(metadata: MetadataCollector, doi: Optional[str]) -> Optional[str]:
    if doi:
        return doi.replace("https://doi.org/", "")
    id_value = [val.property_value for val in metadata.get("identifier").values()]
    candidate = None
    if isinstance(id_value, list):
        candidate = next((v for v in id_value if isinstance(v, str) and "doi.org" in v), None)
    elif isinstance(id_value, str) and "doi.org" in id_value:
        candidate = id_value
    return candidate.replace("https://doi.org/", "") if candidate else None


__all__ = ["get_openalex_work"]