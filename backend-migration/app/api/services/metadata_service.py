"""
Compatibility service entrypoints for metadata extraction.
Routes existing API calls into the new framework runtime layer.
"""
from typing import Optional, Dict, Any, Callable, List

from app.framework.api.metadata_runtime import (
    compare_legacy_and_pipeline_extraction as _framework_compare_legacy_and_pipeline_extraction,
    create_extraction_use_case as _framework_create_extraction_use_case,
    run_extraction as _framework_run_extraction,
    run_extraction_with_progress as _framework_run_extraction_with_progress,
    run_single_property_extraction as _framework_run_single_property_extraction,
)


def _create_extraction_use_case(
    repo_url: str,
    access_token: Optional[str],
    with_enrichment: bool,
):
    """Legacy helper retained for compatibility during migration."""
    return _framework_create_extraction_use_case(
        repo_url=repo_url,
        access_token=access_token,
        with_enrichment=with_enrichment,
    )


def run_extraction(
    repo_url: str,
    schema: str,
    access_token: Optional[str],
    with_enrichment: bool,
) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Run metadata extraction once.
    
    Returns:
        (jsonld_document, enriched_metadata or None)
    """
    return _framework_run_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
        with_enrichment=with_enrichment,
    )


def run_extraction_with_progress(
    repo_url: str,
    schema: str,
    access_token: Optional[str],
    with_enrichment: bool,
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Run metadata extraction with optional progress callbacks.

    progress_callback(step_id, status) is called for each step; step_id is one of
    platform, file_parsing, external_data, llm, jsonld_build; status is "started" or "completed".

    Returns:
        (jsonld_document, enriched_metadata or None)
    """
    return _framework_run_extraction_with_progress(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
        with_enrichment=with_enrichment,
        progress_callback=progress_callback,
    )


def run_single_property_extraction(
    repo_url: str,
    schema: str,
    access_token: Optional[str],
    property_name: str,
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Run extraction with enrichment and project down to a single property's
    value, source, and confidence.

    Returns:
        (extracted_at_iso, [ {profile, value, source, confidence}, ... ])
    """
    return _framework_run_single_property_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
        property_name=property_name,
    )


def compare_legacy_and_pipeline_extraction(
    repo_url: str,
    schema: str,
    access_token: Optional[str],
    with_enrichment: bool,
) -> Dict[str, Any]:
    """Compare legacy and pipeline runtime outputs for migration parity checks."""
    return _framework_compare_legacy_and_pipeline_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
        with_enrichment=with_enrichment,
    )
