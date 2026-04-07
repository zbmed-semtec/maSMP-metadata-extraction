"""Default first-party function plugin stubs for extraction stages."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from app.adapters.factory import PlatformExtractorFactory
from app.adapters.file_parser_adapter import FileParserAdapter
from app.framework.functions.plugin import (
    FunctionContext,
    FunctionPlugin,
    FunctionResult,
    RetryPolicy,
)
from app.domain.services.url_pattern_matcher import URLPatternMatcher


@dataclass(frozen=True)
class _BaseStagePlugin:
    """Shared defaults for stage plugin stubs."""

    id: str
    inputs: Tuple[str, ...] = field(default_factory=tuple)
    outputs: Tuple[str, ...] = field(default_factory=tuple)
    retry_policy: Optional[RetryPolicy] = None
    plugin_metadata: Dict[str, Any] = field(default_factory=dict)

    def run(self, context: FunctionContext) -> FunctionResult:
        """
        Pass-through stub.

        Runtime integration will replace this with concrete stage execution.
        """
        return FunctionResult(payload=context.payload, metadata=context.metadata)


class PlatformExtractionPlugin(_BaseStagePlugin, FunctionPlugin):
    """Stage 1: platform metadata extraction."""

    def __init__(self) -> None:
        super().__init__(
            id="platform_extraction",
            inputs=("repo_url", "access_token"),
            outputs=("metadata",),
            plugin_metadata={"stage": 1, "name": "platform"},
        )

    def run(self, context: FunctionContext) -> FunctionResult:
        """
        Execute real platform extraction using existing adapters.

        Required payload keys:
        - repo_url: repository URL
        Optional payload keys:
        - access_token: auth token for private repos
        - extraction_metadata_collector: collector compatible with adapter contracts
        """
        repo_url = context.payload.get("repo_url")
        if not repo_url:
            raise ValueError("platform_extraction requires 'repo_url' in payload")

        access_token = context.payload.get("access_token")
        collector = context.payload.get("extraction_metadata_collector")

        matcher = URLPatternMatcher()
        platform = matcher.detect_platform(str(repo_url))
        if not platform:
            raise ValueError("Unsupported repository platform. Supported: GitHub, GitLab")

        extractor = PlatformExtractorFactory.create_extractor(str(repo_url), access_token)
        metadata = extractor.extract_platform_metadata(
            str(repo_url),
            access_token=access_token,
            extraction_metadata=collector,
        )

        payload = dict(context.payload)
        payload["metadata"] = metadata
        payload["platform"] = platform
        return FunctionResult(payload=payload, metadata=context.metadata)


class FileParsingPlugin(_BaseStagePlugin, FunctionPlugin):
    """Stage 2: repository file parsing."""

    def __init__(self) -> None:
        super().__init__(
            id="file_parsing",
            inputs=("repo_url", "metadata", "access_token"),
            outputs=("metadata", "doi", "reference_extracted"),
            plugin_metadata={"stage": 2, "name": "file_parsing"},
        )

    def run(self, context: FunctionContext) -> FunctionResult:
        """
        Execute real file parsing using existing file parser adapter.

        Required payload keys:
        - repo_url
        - metadata (from platform extraction stage)
        Optional payload keys:
        - access_token
        - platform (if omitted, detected from repo_url)
        - extraction_metadata_collector
        """
        repo_url = context.payload.get("repo_url")
        if not repo_url:
            raise ValueError("file_parsing requires 'repo_url' in payload")

        metadata = context.payload.get("metadata")
        if metadata is None:
            raise ValueError("file_parsing requires 'metadata' in payload")

        access_token = context.payload.get("access_token")
        collector = context.payload.get("extraction_metadata_collector")
        platform = context.payload.get("platform")

        if not platform:
            matcher = URLPatternMatcher()
            platform = matcher.detect_platform(str(repo_url))
        if not platform:
            raise ValueError("Unsupported repository platform. Supported: GitHub, GitLab")

        parser = FileParserAdapter(platform=str(platform), access_token=access_token)
        updated_metadata, doi, reference_extracted = parser.parse_files(
            str(repo_url),
            metadata,
            access_token=access_token,
            extraction_metadata=collector,
        )

        payload = dict(context.payload)
        payload["metadata"] = updated_metadata
        payload["doi"] = doi
        payload["reference_extracted"] = reference_extracted
        payload["platform"] = platform
        return FunctionResult(payload=payload, metadata=context.metadata)


class ExternalEnrichmentPlugin(_BaseStagePlugin, FunctionPlugin):
    """Stage 3: external data enrichment."""

    def __init__(self) -> None:
        super().__init__(
            id="external_enrichment",
            inputs=("repo_url", "metadata", "doi", "reference_extracted", "access_token"),
            outputs=("metadata",),
            plugin_metadata={"stage": 3, "name": "external_data"},
        )


class LLMEnrichmentPlugin(_BaseStagePlugin, FunctionPlugin):
    """Stage 4: LLM-based enrichment."""

    def __init__(self) -> None:
        super().__init__(
            id="llm_enrichment",
            inputs=("repo_url", "metadata"),
            outputs=("metadata",),
            plugin_metadata={"stage": 4, "name": "llm"},
        )


class SchemaBuildPlugin(_BaseStagePlugin, FunctionPlugin):
    """Stage 5: schema output build."""

    def __init__(self) -> None:
        super().__init__(
            id="schema_build",
            inputs=("metadata", "schema"),
            outputs=("jsonld_document",),
            plugin_metadata={"stage": 5, "name": "jsonld_build"},
        )
