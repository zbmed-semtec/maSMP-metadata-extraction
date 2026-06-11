from __future__ import annotations
import logging
import time
from typing import Optional, Dict, Any, List

import requests

logger = logging.getLogger(__name__)
MAX_RATE_LIMIT_WAIT_SECONDS = 60


class GitLabRateLimitError(Exception):
    def __init__(self, retry_after_seconds: float, message: Optional[str] = None):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(
            message
            or (
                "GitLab API rate limit exceeded. "
                "Use a personal access token (--token or GITLAB_TOKEN) for higher limits, "
                f"or try again in {int(retry_after_seconds)}s."
            )
        )


class GitLabClient:
    BASE_URL = "https://gitlab.com/api/v4"

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.headers = {"Accept": "application/json"}
        if access_token:
            self.headers["PRIVATE-TOKEN"] = access_token

    def rate_limit_get(self, url: str, backoff_rate: int = 2, initial_backoff: int = 1) -> Dict[str, Any]:
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                sleep_time = int(retry_after) if retry_after else initial_backoff
                if not retry_after:
                    initial_backoff *= backoff_rate
                if sleep_time > MAX_RATE_LIMIT_WAIT_SECONDS:
                    raise GitLabRateLimitError(sleep_time)
                logger.warning(f"Rate limit hit. Sleeping {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            response.raise_for_status()

    def get_project(self, project_id: str) -> Dict[str, Any]:
        return self.rate_limit_get(f"{self.BASE_URL}/projects/{project_id}")

    def get_languages(self, project_id: str) -> Dict[str, float]:
        return self.rate_limit_get(f"{self.BASE_URL}/projects/{project_id}/languages")

    def get_contributors(self, project_id: str) -> List[Dict[str, Any]]:
        return self.rate_limit_get(f"{self.BASE_URL}/projects/{project_id}/repository/contributors")

    def get_license(self, project_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.rate_limit_get(f"{self.BASE_URL}/projects/{project_id}?license=true")
        except requests.HTTPError:
            return None

    def get_latest_release(self, project_id: str) -> Optional[Dict[str, Any]]:
        try:
            releases = self.rate_limit_get(f"{self.BASE_URL}/projects/{project_id}/releases")
            return releases[0] if releases else None
        except requests.HTTPError:
            return None

    def get_commits(self, project_id: str, per_page: int = 1) -> List[Dict[str, Any]]:
        return self.rate_limit_get(f"{self.BASE_URL}/projects/{project_id}/repository/commits?per_page={per_page}")
