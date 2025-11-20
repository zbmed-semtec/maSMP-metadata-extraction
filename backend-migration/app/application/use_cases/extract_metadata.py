"""
Layer 2: Application / Use Cases
The orchestration layer - defines the fixed 5-step process.
Only imports from Layer 1 (Core).
Uses dependency injection to get tools from Layer 3.
"""
from typing import Protocol, Optional
from app.core.entities.repository_metadata import RepositoryMetadata


# Protocol definitions for dependency injection (Layer 2 doesn't know about concrete implementations)
class PlatformExtractor(Protocol):
    """Protocol for platform-specific extractors (GitHub, etc.)"""
    def extract_platform_metadata(self, repo_url: str, access_token: Optional[str] = None) -> RepositoryMetadata:
        """Extract metadata from the platform API"""
        ...


class FileParser(Protocol):
    """Protocol for parsing repository files"""
    def parse_files(self, repo_url: str, metadata: RepositoryMetadata, access_token: Optional[str] = None) -> tuple[RepositoryMetadata, Optional[str], bool]:
        """
        Parse repository files (README, CITATION, etc.)
        Returns: (updated_metadata, doi, reference_extracted)
        """
        ...


class ExternalDataFetcher(Protocol):
    """Protocol for fetching external data"""
    def fetch_external_data(self, repo_url: str, metadata: RepositoryMetadata, doi: Optional[str] = None, reference_extracted: bool = False, access_token: Optional[str] = None) -> RepositoryMetadata:
        """Fetch data from external sources (OpenAlex, Wayback, etc.)"""
        ...


class LLMExtractor(Protocol):
    """Protocol for LLM-based extraction"""
    def extract_with_llm(self, metadata: RepositoryMetadata, repo_url: str) -> RepositoryMetadata:
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
        jsonld_builder: JSONLDBuilder
    ):
        """
        Initialize the use case with all required tools.
        
        Args:
            platform_extractor: Extracts metadata from platform API (GitHub, etc.)
            file_parser: Parses repository files
            external_data_fetcher: Fetches external data (OpenAlex, Wayback, etc.)
            llm_extractor: Extracts metadata using LLM
            jsonld_builder: Builds the final JSON-LD document
        """
        self.platform_extractor = platform_extractor
        self.file_parser = file_parser
        self.external_data_fetcher = external_data_fetcher
        self.llm_extractor = llm_extractor
        self.jsonld_builder = jsonld_builder
    
    def execute(
        self,
        repo_url: str,
        schema: str,
        access_token: Optional[str] = None
    ) -> dict:
        """
        Execute the 5-step metadata extraction process.
        
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
            
        Returns:
            dict: JSON-LD document with extracted metadata
        """
        # Step 1: Extract platform metadata
        metadata = self.platform_extractor.extract_platform_metadata(repo_url, access_token)
        
        # Step 2: Parse repository files
        metadata, doi, reference_extracted = self.file_parser.parse_files(
            repo_url, metadata, access_token
        )
        
        # Step 3: Fetch external data
        metadata = self.external_data_fetcher.fetch_external_data(
            repo_url, metadata, doi, reference_extracted, access_token
        )
        
        # Step 4: Extract with LLM (optional enhancement)
        # This step can be skipped if not needed
        try:
            metadata = self.llm_extractor.extract_with_llm(metadata, repo_url)
        except Exception:
            # LLM extraction is optional, continue if it fails
            pass
        
        # Step 5: Build JSON-LD document
        # Determine if there's a release (this info comes from platform extractor)
        has_release = metadata.has_release
        jsonld_document = self.jsonld_builder.build_jsonld(metadata, schema, has_release)
        
        return jsonld_document

