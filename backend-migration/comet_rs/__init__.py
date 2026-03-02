"""
Public Python API for comet_rs.

Provides simple, stable functions for extracting metadata and assessing FAIRness
without exposing internal app.* wiring.
"""
from typing import Any, Dict, Optional, Tuple, Literal

from app.api.services.metadata_service import run_extraction
from app.api.services.fairness_service import run_fairness_assessment
from app.core.entities.fairness import FairnessReport

SchemaLiteral = Literal["maSMP", "CODEMETA"]


def extract_metadata(
    repo_url: str,
    schema: SchemaLiteral = "maSMP",
    *,
    token: Optional[str] = None,
    with_enrichment: bool = False,
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    High-level wrapper to extract maSMP/CODEMETA metadata for a repository.

    Returns:
        (jsonld_document, enriched_metadata or None)
    """
    return run_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=token,
        with_enrichment=with_enrichment,
    )


def assess_fairness(
    repo_url: str,
    schema: SchemaLiteral = "maSMP",
    *,
    token: Optional[str] = None,
) -> Tuple[Dict[str, Any], FairnessReport]:
    """
    Run metadata extraction and FAIRness assessment for a repository.

    Returns:
        (jsonld_document, FairnessReport)
    """
    return run_fairness_assessment(
        repo_url=repo_url,
        schema=schema,
        access_token=token,
        with_enrichment=False,
    )


__all__ = ["extract_metadata", "assess_fairness", "FairnessReport"]

