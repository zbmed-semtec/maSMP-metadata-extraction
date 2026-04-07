"""
Public Python API for comet_rs.

Provides simple, stable functions for extracting metadata and assessing FAIRness
without exposing internal app.* wiring.
"""
from typing import Any, Dict, Optional, Tuple, Literal, List

from app.framework.api import extract_metadata as _framework_extract_metadata
from app.framework.api import extract_property as _framework_extract_property
from app.framework.api import assess_fairness as _framework_assess_fairness
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
    return _framework_extract_metadata(
        repo_url=repo_url,
        schema=schema,
        token=token,
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
    extracted_at, items = _framework_extract_property(
        repo_url=repo_url,
        property_name=property_name,
        schema=schema,
        token=token,
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
    return _framework_assess_fairness(
        repo_url=repo_url,
        schema=schema,
        token=token,
    )


__all__ = ["extract_metadata", "extract_property", "assess_fairness", "FairnessReport"]

