"""
Layer 3: Adapters - Codeberg
Codeberg API client with rate limiting
"""
import requests
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# If rate-limit wait would exceed this (seconds), we raise instead of blocking.
MAX_RATE_LIMIT_WAIT_SECONDS = 60


class CodebergRateLimitError(Exception):
    """Raised when Codeberg rate limit is exceeded and wait time would be too long."""

    def __init__(self, retry_after_seconds: float, message: Optional[str] = None):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            message
            or (
                "Codeberg API rate limit exceeded. "
                "Use a personal access token (--token or CODEBERG_TOKEN) for 5,000 requests/hour, "
                f"or try again in {int(retry_after_seconds)}s."
            )
        )


class CodebergClient:
    """Client for Codeberg API with rate limiting"""
    
    BASE_URL = "https://codeberg.org/api/v1"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Codeberg client.
        
        Args:
            access_token: Codeberg access token
        """
        self.access_token = access_token
        self.headers = {"Accept": "application/vnd.codeberg.v3+json"}
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"
    
    def rate_limit_get(self, url: str, backoff_rate: int = 2, initial_backoff: int = 1) -> Dict[str, Any]:
        """
        Perform rate-limited GET request with exponential backoff.
        
        Args:
            url: API URL
            backoff_rate: Factor to increase backoff time
            initial_backoff: Initial backoff time in seconds
            
        Returns:
            JSON response
        """
        while True:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 403:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    sleep_time = int(retry_after)
                elif "X-RateLimit-Remaining" in response.headers and int(response.headers["X-RateLimit-Remaining"]) == 0:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    sleep_time = max(reset_time - time.time(), 0) + 1
                else:
                    sleep_time = initial_backoff
                    initial_backoff *= backoff_rate

                if sleep_time > MAX_RATE_LIMIT_WAIT_SECONDS:
                    raise CodebergRateLimitError(sleep_time)

                logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            
            response.raise_for_status()
    
    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        return self.rate_limit_get(url)
    
    def get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository languages"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/languages"
        return self.rate_limit_get(url)
    
    def get_contributors(self, owner: str, repo: str) -> list[Dict[str, Any]]:
        """Get repository contributors"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/collaborators"
        return self.rate_limit_get(url)
    
    def get_license(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get repository license"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/license"
        try:
            return self.rate_limit_get(url)
        except requests.exceptions.RequestException:
            return None
    
    def get_latest_release(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get latest release"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/releases/latest"
        try:
            return self.rate_limit_get(url)
        except requests.exceptions.RequestException:
            return None
    
    def get_commits(self, owner: str, repo: str, page: int = 1) -> list[Dict[str, Any]]:
        """Get repository commits"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        params = {"page": page}
        return self.rate_limit_get(url)

