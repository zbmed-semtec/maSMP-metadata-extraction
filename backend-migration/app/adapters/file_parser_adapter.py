"""
Layer 3: Adapters
File parser adapter - implements FileParser protocol
"""
import re
from typing import Optional, Tuple, TYPE_CHECKING

import requests

from app.core.entities.repository_metadata import RepositoryMetadata
from app.domain.services.citation_file_parser import CitationFileParser
from app.domain.services.readme_parser import ReadmeParser
from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.adapters.github.github_file_fetcher import GitHubFileFetcher
from app.adapters.gitlab.gitlab_file_fetcher import GitLabFileFetcher
from app.domain.extraction_sources import (
    SOURCE_CITATION_CFF,
    SOURCE_LICENSE_FILE,
    SOURCE_README_PARSER,
    CONFIDENCE_CITATION,
    CONFIDENCE_LICENSE,
    CONFIDENCE_README,
)

if TYPE_CHECKING:
    from app.application.use_cases.extract_metadata import ExtractionMetadataCollector

# Zenodo badge URLs in raw README (image or link); link redirects to DOI
# e.g. [![DOI](https://zenodo.org/badge/190487675.svg)](https://zenodo.org/badge/latestdoi/198487675)
_ZENODO_BADGE_URL_PATTERN = re.compile(
    r"https://zenodo\.org/badge/(?:latestdoi/)?\d+(?:\.svg)?",
    re.IGNORECASE,
)


def _find_zenodo_badge_url(content: str) -> Optional[str]:
    """Find first Zenodo badge URL in raw README. Prefer latestdoi (link) over badge/ID.svg (image)."""
    latestdoi_matches = re.findall(
        r"https://zenodo\.org/badge/latestdoi/\d+",
        content,
        re.IGNORECASE,
    )
    if latestdoi_matches:
        return latestdoi_matches[0]
    match = _ZENODO_BADGE_URL_PATTERN.search(content)
    return match.group(0) if match else None


def _resolve_zenodo_badge_to_doi(badge_url: str) -> Optional[str]:
    """Resolve Zenodo badge URL (e.g. .../latestdoi/123) to final DOI URL via redirect."""
    try:
        response = requests.get(badge_url, allow_redirects=True, timeout=10)
        if response.url and "doi.org" in response.url:
            return response.url
    except Exception:
        pass
    return None


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
        elif platform == "gitlab":
            self.file_fetcher = GitLabFileFetcher(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def parse_files(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        access_token: Optional[str] = None,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> Tuple[RepositoryMetadata, Optional[str], bool]:
        """
        Parse repository files (CITATION.cff, LICENSE, README).

        Args:
            repo_url: Repository URL
            metadata: Current metadata object
            access_token: Access token (if not set in constructor)
            extraction_metadata: Optional collector for source/confidence per property

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
                if extraction_metadata is not None:
                    for field in ("alternateName", "keywords", "identifier", "citation", "author", "codemeta_referencePublication"):
                        if getattr(metadata, field, None) is not None:
                            extraction_metadata.record(field, SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
                break

        # Try to fetch LICENSE
        for branch in ["main", "master"]:
            license_content = self.file_fetcher.fetch_file_from_repo(owner, repo, "LICENSE", branch)
            if license_content:
                copyright_holder = self.readme_parser.extract_license_copyright(license_content)
                if copyright_holder:
                    metadata.copyrightHolder = copyright_holder
                    if extraction_metadata is not None:
                        extraction_metadata.record("copyrightHolder", SOURCE_LICENSE_FILE, CONFIDENCE_LICENSE)
                break

        # Parse README if reference not already extracted
        if not reference_extracted:
            for branch in ["main", "master"]:
                readme_content = self.file_fetcher.fetch_file_from_repo(owner, repo, "README.md", branch)
                if readme_content:
                    metadata, identifier_set_by_readme = self.readme_parser.parse_readme(
                        readme_content, metadata
                    )
                    # Raw README often has Zenodo badge URLs (not the DOI string); resolve them
                    if not identifier_set_by_readme:
                        zenodo_badge_url = _find_zenodo_badge_url(readme_content)
                        if zenodo_badge_url:
                            resolved_doi = _resolve_zenodo_badge_to_doi(zenodo_badge_url)
                            if resolved_doi:
                                # Merge resolved DOI into identifier list
                                existing_ids = list(metadata.identifier or [])
                                if resolved_doi not in existing_ids:
                                    existing_ids.append(resolved_doi)
                                metadata.identifier = existing_ids
                                identifier_set_by_readme = True
                    if metadata.codemeta_referencePublication:
                        reference_extracted = True
                    if extraction_metadata is not None:
                        if metadata.codemeta_readme is not None:
                            extraction_metadata.record("codemeta_readme", SOURCE_README_PARSER, CONFIDENCE_README)
                        if metadata.codemeta_referencePublication is not None:
                            extraction_metadata.record("codemeta_referencePublication", SOURCE_README_PARSER, CONFIDENCE_README)
                        if metadata.author is not None:
                            extraction_metadata.record("author", SOURCE_README_PARSER, CONFIDENCE_README)
                        if identifier_set_by_readme:
                            extraction_metadata.record("identifier", SOURCE_README_PARSER, CONFIDENCE_README)
                    break

        return metadata, doi, reference_extracted

