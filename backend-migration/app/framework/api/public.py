"""Framework-facing compatibility API for extraction and FAIRness."""

from typing import Any, Dict, List, Optional, Tuple

from app.api.services.fairness_service import run_fairness_assessment
from app.framework.api.metadata_runtime import (
    run_extraction,
    run_single_property_extraction,
)
from app.core.entities.fairness import FairnessReport


def extract_metadata(
    repo_url: str,
    schema: str = "maSMP",
    *,
    token: Optional[str] = None,
    with_enrichment: bool = False,
) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """Compatibility wrapper for metadata extraction."""
    return run_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=token,
        with_enrichment=with_enrichment,
    )


def extract_property(
    repo_url: str,
    property_name: str,
    schema: str = "maSMP",
    *,
    token: Optional[str] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Compatibility wrapper for single-property extraction."""
    return run_single_property_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=token,
        property_name=property_name,
    )


def assess_fairness(
    repo_url: str,
    schema: str = "maSMP",
    *,
    token: Optional[str] = None,
) -> Tuple[Dict[str, Any], FairnessReport]:
    """Compatibility wrapper for FAIRness assessment."""
    return run_fairness_assessment(
        repo_url=repo_url,
        schema=schema,
        access_token=token,
        with_enrichment=False,
    )
