"""Default first-party function plugin stubs for extraction stages."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from app.framework.functions.plugin import (
    FunctionContext,
    FunctionPlugin,
    FunctionResult,
    RetryPolicy,
)


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


class FileParsingPlugin(_BaseStagePlugin, FunctionPlugin):
    """Stage 2: repository file parsing."""

    def __init__(self) -> None:
        super().__init__(
            id="file_parsing",
            inputs=("repo_url", "metadata", "access_token"),
            outputs=("metadata", "doi", "reference_extracted"),
            plugin_metadata={"stage": 2, "name": "file_parsing"},
        )


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
