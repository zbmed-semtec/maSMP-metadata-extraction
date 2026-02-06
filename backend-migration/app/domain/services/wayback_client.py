"""
Layer 3: Domain Services
Wayback Machine client - checks for archived versions
"""
import requests
from typing import Optional
from urllib.parse import urlparse


class WaybackClient:
    """Client for checking Wayback Machine archives"""
    
    @staticmethod
    def check_archive_url(url: str, timeout: int = 5) -> Optional[str]:
        """
        Check if a URL is archived in Wayback Machine.
        
        Args:
            url: URL to check
            timeout: Request timeout in seconds
            
        Returns:
            Archive URL if found, None otherwise
        """
        archive_url = f"https://web.archive.org/web/{url}"
        try:
            response = requests.get(archive_url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return archive_url
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    @staticmethod
    def check_software_heritage(url: str, timeout: int = 5) -> Optional[str]:
        """
        Check if a repository is archived in Software Heritage.
        
        Args:
            url: Repository URL to check
            timeout: Request timeout in seconds
            
        Returns:
            Archive URL if found, None otherwise
        """
        archive_url = f"https://archive.softwareheritage.org/browse/origin/directory/?origin_url={url}"
        try:
            response = requests.get(archive_url, timeout=timeout, allow_redirects=True)
            if response.status_code == 200:
                return archive_url
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    def find_archive(self, repo_url: str) -> Optional[str]:
        """
        Find archive URL from multiple sources.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            Archive URL if found, None otherwise
        """
        # Check Software Heritage first
        swh_url = self.check_software_heritage(repo_url)
        if swh_url:
            return swh_url
        
        # Check Wayback Machine
        wayback_url = self.check_archive_url(repo_url)
        if wayback_url:
            return wayback_url
        
        return None

