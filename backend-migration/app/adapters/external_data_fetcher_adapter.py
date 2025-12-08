"""
Layer 3: Adapters
External data fetcher adapter - implements ExternalDataFetcher protocol
"""
from typing import Optional
from app.core.entities.repository_metadata import RepositoryMetadata, ReferencePublication, Person
from app.domain.services.openalex_client import OpenAlexClient
from app.domain.services.wayback_client import WaybackClient
from app.domain.services.readme_parser import ReadmeParser
from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.adapters.github.github_file_fetcher import GitHubFileFetcher
from app.adapters.gitlab.gitlab_file_fetcher import GitLabFileFetcher


class ExternalDataFetcherAdapter:
    """
    Adapter that implements ExternalDataFetcher protocol.
    Fetches data from external sources (OpenAlex, Wayback, etc.)
    """
    
    def __init__(self, platform: str, access_token: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize external data fetcher adapter.
        
        Args:
            platform: Platform name (github or gitlab)
            access_token: Access token
            base_url: Not used (kept for compatibility)
        """
        self.platform = platform
        self.openalex_client = OpenAlexClient()
        self.wayback_client = WaybackClient()
        self.readme_parser = ReadmeParser()
        self.url_matcher = URLPatternMatcher()
        
        if platform == "github":
            self.file_fetcher = GitHubFileFetcher(access_token)
        elif platform == "gitlab":
            self.file_fetcher = GitLabFileFetcher(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def fetch_external_data(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        doi: Optional[str] = None,
        reference_extracted: bool = False,
        access_token: Optional[str] = None
    ) -> RepositoryMetadata:
        """
        Fetch external data and enrich metadata.
        """
        owner, repo = self.url_matcher.extract_repo_info(repo_url)
        if not owner or not repo:
            return metadata
        
        # Fetch archive information through README
        readme_content = None
        
        for branch in ["main", "master"]:
            
            if self.platform == "github":
                readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            else:  # gitlab
                readme_url = f"https://gitlab.com/{owner}/{repo}/-/raw/{branch}/README.md"

            readme_content = self.file_fetcher.fetch_file_content(readme_url)
            
            if readme_content:
                # Check for Zenodo badges
                zenodo_urls = self.url_matcher.check_zenodo_badge(readme_content)
                if zenodo_urls:
                    metadata.archivedAt = zenodo_urls[0]
                    break
                
                # Check Wayback Machine and Software Heritage
                archive_url = self.wayback_client.find_archive(repo_url)
                if archive_url:
                    metadata.archivedAt = archive_url
                    break
        
        # Enrich with OpenAlex data if DOI is available
        if doi:
            metadata = self.openalex_client.enrich_metadata(metadata, doi)
        
        # Extract DOI reference if not already extracted
        if not reference_extracted and doi:
            work_data = self.openalex_client.fetch_work_by_doi(doi)
            if work_data:
                authors_data = self.openalex_client.extract_authors(work_data)
                authors = []
                
                if authors_data:
                    for author_dict in authors_data:
                        authors.append(Person(
                            type=author_dict.get("@type", "Person"),
                            familyName=author_dict.get("familyName"),
                            givenName=author_dict.get("givenName"),
                            id=author_dict.get("@id")
                        ))
                
                metadata.codemeta_referencePublication = ReferencePublication(
                    type="ScholarlyArticle",
                    id=f"https://doi.org/{doi}",
                    name=work_data.get("title"),
                    author=authors if authors else None
                )
        
        return metadata
