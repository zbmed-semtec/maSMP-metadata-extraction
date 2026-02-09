"""
Layer 2: Application / Use Cases
The orchestration layer - defines the fixed 5-step process.
Only imports from Layer 1 (Core).
Uses dependency injection to get tools from Layer 3.
"""
from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any, Callable
from app.core.entities.repository_metadata import RepositoryMetadata

# Step IDs for progress streaming (used by SSE endpoint and frontend)
EXTRACTION_STEPS = [
    ("platform", "Extracting from platform API (GitHub/GitLab)"),
    ("file_parsing", "Parsing repository files"),
    ("external_data", "Fetching external data (OpenAlex, Wayback)"),
    ("llm", "Extracting with LLM"),
    ("jsonld_build", "Building JSON-LD document"),
]


# ---------------------------------------------------------------------------
# Extraction metadata collector (optional enrichment for UI)
# ---------------------------------------------------------------------------

class ExtractionMetadataCollector(Protocol):
    """
    Protocol for collecting per-property extraction metadata (source, confidence).
    Used to enrich the API response for UI display; not included in the JSON-LD download.
    """
    def record(self, entity_field: str, source: str, confidence: float) -> None:
        """Record that a property was set by the given source with the given confidence."""
        ...

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Return all records: entity_field -> {source, confidence}."""
        ...


@dataclass(frozen=True)
class ExtractMetadataResult:
    """Result of the extract metadata use case: JSON-LD document and optional extraction metadata."""
    jsonld_document: dict
    extraction_metadata: Dict[str, Dict[str, Any]]  # entity_field -> {source, confidence}


# Protocol definitions for dependency injection (Layer 2 doesn't know about concrete implementations)
class PlatformExtractor(Protocol):
    """Protocol for platform-specific extractors (GitHub, etc.)"""
    def extract_platform_metadata(
        self,
        repo_url: str,
        access_token: Optional[str] = None,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> RepositoryMetadata:
        """Extract metadata from the platform API"""
        ...


class FileParser(Protocol):
    """Protocol for parsing repository files"""
    def parse_files(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        access_token: Optional[str] = None,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> tuple[RepositoryMetadata, Optional[str], bool]:
        """
        Parse repository files (README, CITATION, etc.)
        Returns: (updated_metadata, doi, reference_extracted)
        """
        ...


class ExternalDataFetcher(Protocol):
    """Protocol for fetching external data"""
    def fetch_external_data(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        doi: Optional[str] = None,
        reference_extracted: bool = False,
        access_token: Optional[str] = None,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> RepositoryMetadata:
        """Fetch data from external sources (OpenAlex, Wayback, etc.)"""
        ...


class LLMExtractor(Protocol):
    """Protocol for LLM-based extraction"""
    def extract_with_llm(
        self,
        metadata: RepositoryMetadata,
        repo_url: str,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> RepositoryMetadata:
        """Extract additional metadata using LLM"""
        ...


class JSONLDBuilder(Protocol):
    """Protocol for building JSON-LD documents"""
    def build_jsonld(self, metadata: RepositoryMetadata, schema: str, has_release: bool) -> dict:
        """Build JSON-LD document from metadata"""
        ...


class ExtractMetadataUseCase:
    """
    The main use case - orchestrates the 5-step metadata extraction process.
    
    This is the "chef" that coordinates all the tools but doesn't create them.
    Tools are injected via dependency injection.
    """
    
    def __init__(
        self,
        platform_extractor: PlatformExtractor,
        file_parser: FileParser,
        external_data_fetcher: ExternalDataFetcher,
        llm_extractor: LLMExtractor,
        jsonld_builder: JSONLDBuilder,
        extraction_metadata_collector: Optional[ExtractionMetadataCollector] = None,
    ):
        """
        Initialize the use case with all required tools.
        
        Args:
            platform_extractor: Extracts metadata from platform API (GitHub, etc.)
            file_parser: Parses repository files
            external_data_fetcher: Fetches external data (OpenAlex, Wayback, etc.)
            llm_extractor: Extracts metadata using LLM
            jsonld_builder: Builds the final JSON-LD document
            extraction_metadata_collector: Optional collector for source/confidence per property (for UI)
        """
        self.platform_extractor = platform_extractor
        self.file_parser = file_parser
        self.external_data_fetcher = external_data_fetcher
        self.llm_extractor = llm_extractor
        self.jsonld_builder = jsonld_builder
        self.extraction_metadata_collector = extraction_metadata_collector
    
    def execute(
        self,
        repo_url: str,
        schema: str,
        access_token: Optional[str] = None,
        progress_callback: Optional[Callable[[str, str], None]] = None,
    ) -> ExtractMetadataResult:
        """
        Execute the 5-step metadata extraction process.

        Optionally reports progress via progress_callback(step_id, status)
        where status is "started" or "completed". Step IDs: platform, file_parsing,
        external_data, llm, jsonld_build.

        This is the fixed orchestration - the order never changes:
        1. Extract platform metadata (API)
        2. Parse repository files (README, CITATION, etc.)
        3. Fetch external data (OpenAlex, Wayback, etc.)
        4. Extract with LLM (if needed)
        5. Build JSON-LD document

        Args:
            repo_url: URL of the repository
            schema: Schema to use (maSMP or CODEMETA)
            access_token: Optional access token for private repositories
            progress_callback: Optional callback(step_id, status) for streaming progress

        Returns:
            ExtractMetadataResult with jsonld_document and extraction_metadata (for UI enrichment)
        """
        def report(step_id: str, status: str) -> None:
            if progress_callback:
                progress_callback(step_id, status)

        collector = self.extraction_metadata_collector

        # Step 1: Extract platform metadata
        report("platform", "started")
        metadata = self.platform_extractor.extract_platform_metadata(
            repo_url, access_token, extraction_metadata=collector
        )
        report("platform", "completed")

        # Step 2: Parse repository files
        report("file_parsing", "started")
        metadata, doi, reference_extracted = self.file_parser.parse_files(
            repo_url, metadata, access_token, extraction_metadata=collector
        )
        report("file_parsing", "completed")

        # Step 3: Fetch external data
        report("external_data", "started")
        metadata = self.external_data_fetcher.fetch_external_data(
            repo_url, metadata, doi, reference_extracted, access_token,
            extraction_metadata=collector
        )
        report("external_data", "completed")

        # Step 4: Extract with LLM (optional enhancement)
        report("llm", "started")
        try:
            metadata = self.llm_extractor.extract_with_llm(
                metadata, repo_url, extraction_metadata=collector
            )
        except Exception:
            pass
        report("llm", "completed")

        # Step 5: Build JSON-LD document
        report("jsonld_build", "started")
        has_release = metadata.has_release
        jsonld_document = self.jsonld_builder.build_jsonld(metadata, schema, has_release)
        report("jsonld_build", "completed")

        extraction_metadata = collector.get_all() if collector else {}
        return ExtractMetadataResult(
            jsonld_document=jsonld_document,
            extraction_metadata=extraction_metadata,
        )

