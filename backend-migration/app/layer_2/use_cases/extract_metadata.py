"""
Layer 2 — Application / use cases (`app.layer_2`).
Orchestration: compose and run extraction pipeline, then build JSON-LD.
"""
from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any, Callable

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_ARCHIVE,
    CONFIDENCE_CITATION,
    CONFIDENCE_LICENSE,
    CONFIDENCE_OPENALEX,
    CONFIDENCE_PLATFORM,
    CONFIDENCE_README,
    SOURCE_CITATION_CFF,
    SOURCE_GITHUB_API,
    SOURCE_GITLAB_API,
    SOURCE_LICENSE_FILE,
    SOURCE_OPENALEX,
    SOURCE_README_PARSER,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_WAYBACK,
    SOURCE_ZENODO_BADGE,
)
from app.layer_3.composers import PipelineComposer
from app.layer_3.extraction_metadata import ExtractionMetadataCollector
from app.layer_3.steps.contracts import ExtractionPipelineRunner, StepContext, StepState
from app.layer_3.utils.url_pattern_matcher import URLPatternMatcher

# Step IDs for progress streaming (used by SSE endpoint and frontend)
EXTRACTION_STEPS = [
    ("pipeline", "Running extraction pipeline"),
    ("jsonld_build", "Building JSON-LD document"),
]


# ---------------------------------------------------------------------------
# Extraction metadata collector (optional enrichment for UI)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExtractMetadataResult:
    """
    Result of the extract metadata use case.

    Exposes both the final JSON-LD document (for API/CLI consumers) and
    the internal SoftwareMetadata instance so that other services
    (e.g. FAIRness assessment) can perform schema-independent analysis.
    """
    jsonld_document: dict
    extraction_metadata: Dict[str, Dict[str, Any]]  # entity_field -> {source, confidence}
    metadata: SoftwareMetadata


class JSONLDBuilder(Protocol):
    """Protocol for building JSON-LD documents"""
    def build_jsonld(self, metadata: SoftwareMetadata, schema: str, has_release: bool) -> dict:
        """Build JSON-LD document from metadata"""
        ...


class ExtractMetadataUseCase:
    """
    The main use case: compose a Layer 3 pipeline, run it, then export JSON-LD.
    """
    
    def __init__(
        self,
        jsonld_builder: JSONLDBuilder,
        pipeline_composer: Optional[PipelineComposer] = None,
        pipeline_runner: Optional[ExtractionPipelineRunner] = None,
        extraction_metadata_collector: Optional[ExtractionMetadataCollector] = None,
    ):
        """
        Initialize the use case with all required tools.
        
        Args:
            jsonld_builder: Builds the final JSON-LD document
            pipeline_composer: Selects the extraction pipeline profile
            pipeline_runner: Runs the composed extraction pipeline
            extraction_metadata_collector: Optional collector for source/confidence per property (for UI)
        """
        self.jsonld_builder = jsonld_builder
        self.pipeline_composer = pipeline_composer or PipelineComposer()
        self.pipeline_runner = pipeline_runner or ExtractionPipelineRunner()
        self.extraction_metadata_collector = extraction_metadata_collector
    
    def execute(
        self,
        repo_url: str,
        schema: str,
        access_token: Optional[str] = None,
        progress_callback: Optional[Callable[[str, str], None]] = None,
    ) -> ExtractMetadataResult:
        """
        Execute metadata extraction for one repository.

        Optionally reports progress via progress_callback(step_id, status)
        where status is "started" or "completed".

        Args:
            repo_url: URL of the repository
            schema: Schema to use (maSMP or CODEMETA)
            access_token: Optional access token for private repositories
            progress_callback: Optional callback(step_id, status) for streaming progress

        Returns:
            ExtractMetadataResult with jsonld_document and extraction_metadata (for UI enrichment)
        """
        collector = self.extraction_metadata_collector
        platform = URLPatternMatcher.detect_platform(repo_url)
        if not platform:
            raise ValueError("Unsupported repository platform. Supported: GitHub, GitLab")

        if progress_callback:
            progress_callback("pipeline", "started")
        
        state = StepState(
            metadata=SoftwareMetadata(),
            data={
                "record_field": _build_record_field(collector, platform),
            },
        )
        context = StepContext(
            repo_url=repo_url,
            domain="software",
            schema=schema,
            platform=platform,
            access_token=access_token,
        )

        pipeline = self.pipeline_composer.compose(context)
        
        metadata = self.pipeline_runner.run(pipeline, context, state).metadata

        if progress_callback:
            progress_callback("pipeline", "completed")

        # Step 5: Build JSON-LD document
        if progress_callback:
            progress_callback("jsonld_build", "started")
        has_release = metadata.has_release
        jsonld_document = self.jsonld_builder.build_jsonld(metadata, schema, has_release)
        if progress_callback:
            progress_callback("jsonld_build", "completed")

        extraction_metadata = collector.get_all() if collector else {}
        return ExtractMetadataResult(
            jsonld_document=jsonld_document,
            extraction_metadata=extraction_metadata,
            metadata=metadata,
        )


def _build_record_field(
    collector: Optional[ExtractionMetadataCollector],
    platform: str,
) -> Callable[[str], None]:
    platform_source = SOURCE_GITHUB_API if platform == "github" else SOURCE_GITLAB_API

    def record(
        field: str,
        *,
        source: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> None:
        if collector is None:
            return
        collector.record(
            field,
            source if source is not None else _source_for_field(field, platform_source),
            confidence if confidence is not None else _confidence_for_field(field),
        )

    return record


def _source_for_field(field: str, platform_source: str) -> str:
    if field in {
        "author",
        "alternateName",
        "identifier",
        "codemeta_referencePublication",
        "citation",
    }:
        return SOURCE_CITATION_CFF
    if field == "copyrightHolder":
        return SOURCE_LICENSE_FILE
    if field in {"archivedAt"}:
        return SOURCE_ZENODO_BADGE
    return platform_source


def _confidence_for_field(field: str) -> float:
    if field in {
        "author",
        "alternateName",
        "identifier",
        "codemeta_referencePublication",
        "citation",
    }:
        return CONFIDENCE_CITATION
    if field == "copyrightHolder":
        return CONFIDENCE_LICENSE
    if field in {"archivedAt"}:
        return CONFIDENCE_ARCHIVE
    return CONFIDENCE_PLATFORM

