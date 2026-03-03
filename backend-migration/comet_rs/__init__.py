"""
Public Python API for comet_rs.

Provides simple, stable functions for extracting metadata and assessing FAIRness
without exposing internal app.* wiring.
"""
from typing import Any, Dict, Optional, Tuple, Literal, List

from app.api.services.metadata_service import run_extraction, run_single_property_extraction
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


def extract_property(
    repo_url: str,
    property_name: str,
    schema: SchemaLiteral = "maSMP",
    *,
    token: Optional[str] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract a single property (value + source + confidence) for a repository.

    Returns:
        (extracted_at_iso, [ {profile, value, source, confidence}, ... ])

    For maSMP, the property may be present in both SoftwareSourceCode and
    SoftwareApplication profiles; all matches are returned. For CODEMETA,
    a single synthetic \"codemeta\" profile is used.
    """
    extracted_at, items = run_single_property_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=token,
        property_name=property_name,
    )
    return extracted_at, items


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


__all__ = ["extract_metadata", "extract_property", "assess_fairness", "FairnessReport"]

