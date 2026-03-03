"""
Metadata + FAIRness service.

Provides a single entry point for running extraction and FAIRness assessment
for CLI, HTTP API, and the public Python API.

FAIRness scores are computed from the internal RepositoryMetadata entity so
that they are invariant to the exported schema (maSMP vs CODEMETA). The
schema still controls the shape of the JSON-LD returned alongside the report.
"""
from typing import Dict, Optional, Tuple

from app.application.use_cases.extract_metadata import ExtractMetadataUseCase
from app.core.entities.fairness import FairnessReport
from app.domain.services.fairness_evaluator import evaluate_fairness_from_metadata
from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.adapters.factory import PlatformExtractorFactory
from app.adapters.file_parser_adapter import FileParserAdapter
from app.adapters.external_data_fetcher_adapter import ExternalDataFetcherAdapter
from app.adapters.jsonld_builder import JSONLDBuilder
from app.adapters.extraction_metadata_collector import InMemoryExtractionMetadataCollector
from app.domain.services.llm_extractor import LLMExtractor


_llm_extractor = LLMExtractor()
_jsonld_builder = JSONLDBuilder()


def run_fairness_assessment(
    repo_url: str,
    schema: str,
    access_token: Optional[str] = None,
    with_enrichment: bool = False,
) -> Tuple[Dict, FairnessReport]:
    """
    Run metadata extraction and FAIRness assessment once.

    FAIRness is computed from the unified RepositoryMetadata, so scores do not
    depend on whether maSMP or CODEMETA is chosen. The JSON-LD document that
    is returned does respect the requested schema.

    Returns:
        (jsonld_document, fairness_report)
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

    result = use_case.execute(
        repo_url=repo_url,
        schema=schema,
        access_token=access_token,
    )

    jsonld_document = result.jsonld_document
    fairness_report = evaluate_fairness_from_metadata(result.metadata)
    return jsonld_document, fairness_report

