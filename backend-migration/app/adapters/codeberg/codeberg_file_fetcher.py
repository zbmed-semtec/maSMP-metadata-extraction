"""
Layer 3: Adapters - Codeberg
Codeberg file fetcher - fetches files from Codeberg repositories
"""
import requests
from typing import Optional
from urllib.parse import urlparse
from base64 import b64decode


class CodebergFileFetcher:
    """Fetches files from Codeberg repositories"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize file fetcher.
        
        Args:
            access_token: Codeberg access token
        """
        self.access_token = access_token
        self.headers = {}
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"
    
    def fetch_file_content(self, url: str) -> Optional[str]:
        """
        Fetch file content from Codeberg.
        
        Args:
            url: File URL (api.codeberg.org/api/v1)
            
        Returns:
            File content or None if not found
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException:
            pass
        return None
    
    def fetch_file_from_repo(self, owner: str, repo: str, file_path: str, branch: str = None) -> Optional[str]:
        """
        Fetch file from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to file (e.g., "README.md")
            branch: Branch name
            
        Returns:
            File content or None
        """
        url = f"https://codeberg.org/api/v1/repos/{owner}/{repo}/contents/{file_path}"
        if branch:
            url += f"?ref={branch}"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if not res.ok:
                return None
            res = res.json()
            return b64decode(res.get('content', '')).decode()
        except requests.exceptions.RequestException:
            pass
    
    def list_repo_contents(self, owner: str, repo: str, path: str = "") -> Optional[list]:
        """
        List repository contents.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path in repository
            
        Returns:
            List of file/directory info or None
        """
        url = f"https://codeberg.org/api/v1/repos/{owner}/{repo}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    def is_file_reachable(self, url: str) -> bool:
        """
        Check if a file URL is reachable.
        
        Args:
            url: File URL
            
        Returns:
            True if reachable, False otherwise
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

