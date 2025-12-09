"""
Layer 3: Adapters
File parser adapter - implements FileParser protocol
"""
from typing import Optional, Tuple
from app.core.entities.repository_metadata import RepositoryMetadata
from app.domain.services.citation_file_parser import CitationFileParser
from app.domain.services.readme_parser import ReadmeParser
from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.adapters.github.github_file_fetcher import GitHubFileFetcher


class FileParserAdapter:
    """
    Adapter that implements FileParser protocol.
    Uses platform-specific file fetchers and domain services.
    """
    
    def __init__(self, platform: str, access_token: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize file parser adapter.
        
        Args:
            platform: Platform name (github)
            access_token: Access token
            base_url: Not used (kept for compatibility)
        """
        self.platform = platform
        self.citation_parser = CitationFileParser()
        self.readme_parser = ReadmeParser()
        self.url_matcher = URLPatternMatcher()
        
        if platform == "github":
            self.file_fetcher = GitHubFileFetcher(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def parse_files(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        access_token: Optional[str] = None
    ) -> Tuple[RepositoryMetadata, Optional[str], bool]:
        """
        Parse repository files (CITATION.cff, LICENSE, README).
        
        Args:
            repo_url: Repository URL
            metadata: Current metadata object
            access_token: Access token (if not set in constructor)
            
        Returns:
            tuple: (updated_metadata, doi, reference_extracted)
        """
        owner, repo = self.url_matcher.extract_repo_info(repo_url)
        if not owner or not repo:
            return metadata, None, False
        
        doi = None
        reference_extracted = False
        
        # Try to fetch CITATION.cff
        for branch in ["main", "master"]:
            citation_content = self.file_fetcher.fetch_file_from_repo(owner, repo, "CITATION.cff", branch)
            if citation_content:
                metadata, doi, reference_extracted = self.citation_parser.parse_citation_cff(
                    citation_content, metadata
                )
                break
        
        # Try to fetch LICENSE
        for branch in ["main", "master"]:
            license_content = self.file_fetcher.fetch_file_from_repo(owner, repo, "LICENSE", branch)
            if license_content:
                copyright_holder = self.readme_parser.extract_license_copyright(license_content)
                if copyright_holder:
                    metadata.copyrightHolder = copyright_holder
                break
        
        # Parse README if reference not already extracted
        if not reference_extracted:
            for branch in ["main", "master"]:
                readme_content = self.file_fetcher.fetch_file_from_repo(owner, repo, "README.md", branch)
                
                if readme_content:
                    metadata = self.readme_parser.parse_readme(readme_content, metadata)
                    # If README parsing found references, mark as extracted
                    if metadata.codemeta_referencePublication:
                        reference_extracted = True
                    break
        
        return metadata, doi, reference_extracted

