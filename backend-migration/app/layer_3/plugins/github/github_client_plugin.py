import logging
import time
from typing import Optional, Dict, Any
import requests

from app.layer_2.base_plugin import BasePlugin

logger = logging.getLogger(__name__)
MAX_RATE_LIMIT_WAIT_SECONDS = 60


class GitHubRateLimitError(Exception):
    def __init__(self, retry_after_seconds: float, message: Optional[str] = None):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            message
            or (
                "GitHub API rate limit exceeded. "
                "Use a personal access token (--token or GITHUB_TOKEN) for 5,000 requests/hour, "
                f"or try again in {int(retry_after_seconds)}s."
            )
        )


class GitHubClient(BasePlugin):

    name = "github-client-plugin"
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"

    def rate_limit_get(self, url: str, backoff_rate: int = 2, initial_backoff: int = 1) -> Dict[str, Any]:
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
                    raise GitHubRateLimitError(sleep_time)
                logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            response.raise_for_status()

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        return self.rate_limit_get(f"{self.BASE_URL}/repos/{owner}/{repo}")

    def get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        return self.rate_limit_get(f"{self.BASE_URL}/repos/{owner}/{repo}/languages")

    def get_contributors(self, owner: str, repo: str) -> list[Dict[str, Any]]:
        return self.rate_limit_get(f"{self.BASE_URL}/repos/{owner}/{repo}/contributors")

    def get_license(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        try:
            return self.rate_limit_get(f"{self.BASE_URL}/repos/{owner}/{repo}/license")
        except requests.exceptions.RequestException:
            return None

    def get_latest_release(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        try:
            return self.rate_limit_get(f"{self.BASE_URL}/repos/{owner}/{repo}/releases/latest")
        except requests.exceptions.RequestException:
            return None

    def get_commits(self, owner: str, repo: str, per_page: int = 1) -> list[Dict[str, Any]]:
        return self.rate_limit_get(f"{self.BASE_URL}/repos/{owner}/{repo}/commits")
