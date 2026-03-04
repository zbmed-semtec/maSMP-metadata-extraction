"""
Metadata extraction service: wires adapters and use case, runs extraction.
Single place for composition; endpoints call this instead of building the use case themselves.
"""
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List

from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.adapters.factory import PlatformExtractorFactory
from app.adapters.file_parser_adapter import FileParserAdapter
from app.adapters.external_data_fetcher_adapter import ExternalDataFetcherAdapter
from app.adapters.jsonld_builder import JSONLDBuilder
from app.adapters.extraction_metadata_collector import InMemoryExtractionMetadataCollector
from app.domain.services.llm_extractor import LLMExtractor
from app.application.use_cases.extract_metadata import ExtractMetadataUseCase
from app.api.builders.enriched_metadata import build_enriched_metadata


# Stateless components (created once, reused)
_llm_extractor = LLMExtractor()
_jsonld_builder = JSONLDBuilder()


def _create_extraction_use_case(
    repo_url: str,
    access_token: Optional[str],
    with_enrichment: bool,
) -> tuple[ExtractMetadataUseCase, Optional[InMemoryExtractionMetadataCollector]]:
    """
    Internal helper to create a fully-wired ExtractMetadataUseCase plus optional collector.

    This centralises the orchestration wiring so that different services
    (plain extraction, extraction with progress, FAIRness assessment, etc.)
    can all share the same composition.
    """
    url_matcher = URLPatternMatcher()
    platform = url_matcher.detect_platform(repo_url)
    if not platform:
        raise ValueError("Unsupported repository platform. Supported: GitHub, GitLab")

    platform_extractor = PlatformExtractorFactory.create_extractor(repo_url, access_token)
    file_parser = FileParserAdapter(platform, access_token)
    external_data_fetcher = ExternalDataFetcherAdapter(platform, access_token)
    collector = InMemoryExtractionMetadataCollector() if with_enrichment else None

    use_case = ExtractMetadataUseCase(
        platform_extractor=platform_extractor,
        file_parser=file_parser,
        external_data_fetcher=external_data_fetcher,
        llm_extractor=_llm_extractor,
        jsonld_builder=_jsonld_builder,
        extraction_metadata_collector=collector,
    )

    return use_case, collector


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
    use_case, collector = _create_extraction_use_case(
        repo_url=repo_url,
        access_token=access_token,
        with_enrichment=with_enrichment,
    )

    result = use_case.execute(repo_url=repo_url, schema=schema, access_token=access_token)
    jsonld_document = result.jsonld_document

    if with_enrichment and result.extraction_metadata:
        enriched = build_enriched_metadata(
            jsonld_document,
            result.extraction_metadata,
            schema,
        )
        return jsonld_document, enriched
    return jsonld_document, None


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
    use_case, collector = _create_extraction_use_case(
        repo_url=repo_url,
        access_token=access_token,
        with_enrichment=with_enrichment,
    )

    result = use_case.execute(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
        progress_callback=progress_callback,
    )
    jsonld_document = result.jsonld_document

    if with_enrichment and result.extraction_metadata:
        enriched = build_enriched_metadata(
            jsonld_document,
            result.extraction_metadata,
            schema,
        )
        return jsonld_document, enriched
    return jsonld_document, None


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
    jsonld_document, enriched = run_extraction(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
        with_enrichment=True,
    )

    extracted_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    results: List[Dict[str, Any]] = []

    enriched = enriched or {}

    if schema == "CODEMETA":
        value = jsonld_document.get(property_name)
        profile_key = "codemeta"
        profile_meta = enriched.get(profile_key, {})
        record = profile_meta.get(property_name, {})
        results.append(
            {
                "profile": profile_key,
                "value": value,
                "source": record.get("source"),
                "confidence": record.get("confidence"),
            }
        )
        return extracted_at, results

    # maSMP profiles – property may appear in SoftwareSourceCode and/or SoftwareApplication
    for profile_key in ("maSMP:SoftwareSourceCode", "maSMP:SoftwareApplication"):
        profile_data = jsonld_document.get(profile_key)
        if not isinstance(profile_data, dict):
            continue
        if property_name not in profile_data:
            continue
        value = profile_data.get(property_name)
        profile_meta = enriched.get(profile_key, {})
        record = profile_meta.get(property_name, {})
        results.append(
            {
                "profile": profile_key,
                "value": value,
                "source": record.get("source"),
                "confidence": record.get("confidence"),
            }
        )

    return extracted_at, results
