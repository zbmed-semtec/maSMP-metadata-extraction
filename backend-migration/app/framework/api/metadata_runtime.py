"""Framework-internal metadata runtime with legacy-compatible behavior."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.adapters.extraction_metadata_collector import InMemoryExtractionMetadataCollector
from app.adapters.external_data_fetcher_adapter import ExternalDataFetcherAdapter
from app.adapters.factory import PlatformExtractorFactory
from app.adapters.file_parser_adapter import FileParserAdapter
from app.adapters.jsonld_builder import JSONLDBuilder
from app.api.builders.enriched_metadata import build_enriched_metadata
from app.application.use_cases.extract_metadata import ExtractMetadataUseCase
from app.domain.services.llm_extractor import LLMExtractor
from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.framework.schemas import (
    SchemaBuildContext,
    SchemaEnrichmentContext,
    canonical_schema_name,
    create_default_schema_registry,
    resolve_schema_plugin,
)
from app.framework.pipeline import PipelineRuntimeConfig, resolve_pipeline_definition

# Stateless components (created once, reused)
_llm_extractor = LLMExtractor()
_jsonld_builder = JSONLDBuilder()
_schema_registry = create_default_schema_registry()
_pipeline_runtime_config = PipelineRuntimeConfig()


def get_active_pipeline_definition():
    """
    Resolve the active validated pipeline definition.

    This is a runtime configuration entry point only; execution remains legacy for now.
    """
    return resolve_pipeline_definition(_pipeline_runtime_config)


def _build_enriched_metadata_via_plugin(
    jsonld_document: Dict[str, Any],
    extraction_metadata: Dict[str, Dict[str, Any]],
    schema: str,
) -> Dict[str, Any]:
    """
    Build enrichment through schema plugins with a safe legacy fallback.

    This keeps behavior stable while migrating enrichment logic to plugins.
    """
    try:
        plugin = resolve_schema_plugin(_schema_registry, schema)
        return plugin.enrich_output(
            SchemaEnrichmentContext(
                jsonld_document=jsonld_document,
                extraction_metadata=extraction_metadata,
                raw_schema=schema,
            )
        )
    except ValueError:
        pass
    except Exception:
        # Keep existing behavior if plugin-based enrichment fails at runtime.
        pass
    return build_enriched_metadata(jsonld_document, extraction_metadata, schema)


def _build_jsonld_via_plugin(
    metadata: Any,
    schema: str,
    fallback_jsonld: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build JSON-LD via schema plugin with fallback to existing use-case output.

    This allows plugin-backed schema output without changing current behavior.
    """
    try:
        plugin = resolve_schema_plugin(_schema_registry, schema)
        has_release = bool(getattr(metadata, "has_release", False))
        return plugin.build_output(
            SchemaBuildContext(
                metadata=metadata,
                has_release=has_release,
                raw_schema=schema,
            )
        )
    except ValueError:
        pass
    except Exception:
        # Keep existing output if plugin path fails.
        pass
    return fallback_jsonld


def create_extraction_use_case(
    repo_url: str,
    access_token: Optional[str],
    with_enrichment: bool,
) -> tuple[ExtractMetadataUseCase, Optional[InMemoryExtractionMetadataCollector]]:
    """Create a fully wired extraction use case and optional enrichment collector."""
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
    """Run metadata extraction once and optionally enrich UI metadata fields."""
    schema = canonical_schema_name(_schema_registry, schema)
    use_case, _collector = create_extraction_use_case(
        repo_url=repo_url,
        access_token=access_token,
        with_enrichment=with_enrichment,
    )

    result = use_case.execute(repo_url=repo_url, schema=schema, access_token=access_token)
    jsonld_document = _build_jsonld_via_plugin(
        metadata=result.metadata,
        schema=schema,
        fallback_jsonld=result.jsonld_document,
    )

    if with_enrichment and result.extraction_metadata:
        enriched = _build_enriched_metadata_via_plugin(
            jsonld_document=jsonld_document,
            extraction_metadata=result.extraction_metadata,
            schema=schema,
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
    """Run metadata extraction with optional step-level progress callbacks."""
    schema = canonical_schema_name(_schema_registry, schema)
    use_case, _collector = create_extraction_use_case(
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
    jsonld_document = _build_jsonld_via_plugin(
        metadata=result.metadata,
        schema=schema,
        fallback_jsonld=result.jsonld_document,
    )

    if with_enrichment and result.extraction_metadata:
        enriched = _build_enriched_metadata_via_plugin(
            jsonld_document=jsonld_document,
            extraction_metadata=result.extraction_metadata,
            schema=schema,
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
    Run extraction with enrichment and project to a single property's metadata.

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
