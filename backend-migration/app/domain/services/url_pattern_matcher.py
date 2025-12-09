"""
Layer 3: Domain Services
URL pattern matcher - utility for matching and extracting info from URLs
"""
import re
from urllib.parse import urlparse
from typing import Optional, Tuple


class URLPatternMatcher:
    """Utility class for URL pattern matching and extraction"""
    
    @staticmethod
    def extract_repo_info(repo_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract owner and repository name from a repository URL.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            tuple: (owner, repo_name) or (None, None) if extraction fails
        """
        parsed_url = urlparse(repo_url)
        parts = parsed_url.path.strip("/").split("/")
        if len(parts) < 2:
            return None, None
        return parts[-2], parts[-1]
    
    @staticmethod
    def detect_platform(repo_url: str) -> Optional[str]:
        """
        Detect the platform from a repository URL.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            Platform name (github) or None
        """
        parsed_url = urlparse(repo_url)
        netloc = parsed_url.netloc.lower()
        
        if "github.com" in netloc:
            return "github"
        
        return None
    
    @staticmethod
    def check_zenodo_badge(content: str) -> list[str]:
        """
        Check for Zenodo badge links in content.
        
        Args:
            content: Content to search (e.g., README content)
            
        Returns:
            List of Zenodo DOI URLs
        """
        zenodo_pattern = r"https://(?:doi\.org/(\d+\.\d+/zenodo\.\d+)|zenodo\.org/records/(\d+))"
        matches = re.findall(zenodo_pattern, content)
        extracted_ids = {doi if doi else f"10.5281/zenodo.{record_id}" for doi, record_id in matches}
        extracted_urls = {f"https://doi.org/{doi}" for doi in extracted_ids}
        return list(extracted_urls)

