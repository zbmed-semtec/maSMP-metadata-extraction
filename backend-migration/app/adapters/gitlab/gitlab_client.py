"""
Layer 3: Adapters - gitlab
gitlab API client with rate limiting
"""

import requests
import time
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class GitLabClient:
    """
    Client for interacting with the GitLab API with automatic rate-limit handling.
    Provides individual methods to extract project-level metadata.
    """

    BASE_URL = "https://gitlab.com/api/v4"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitLab API client.

        Args:
            access_token (str | None): Personal access token for GitLab API.
        """
        self.access_token = access_token
        self.headers = {"Accept": "application/json"}

        if access_token:
            self.headers["PRIVATE-TOKEN"] = access_token

    def rate_limit_get(
        self,
        url: str,
        backoff_rate: int = 2,
        initial_backoff: int = 1
    ) -> Dict[str, Any]:
        """
        Perform a GET request with rate-limit handling using exponential backoff.

        Args:
            url (str): Full GitLab API URL.
            backoff_rate (int): Backoff multiplier when retrying.
            initial_backoff (int): Initial sleep time in seconds.

        Returns:
            dict: JSON response content.

        Raises:
            requests.HTTPError: If an unrecoverable status code occurs.
        """
        while True:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    sleep_time = int(retry_after)
                else:
                    sleep_time = initial_backoff
                    initial_backoff *= backoff_rate

                logger.warning(f"Rate limit hit. Sleeping {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue

            response.raise_for_status()


    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata for a GitLab project.

        Args:
            project_id (str): GitLab project ID or URL-encoded namespace path.

        Returns:
            dict: Project metadata.
        """
        url = f"{self.BASE_URL}/projects/{project_id}"
        return self.rate_limit_get(url)

    def get_languages(self, project_id: str) -> Dict[str, float]:
        """
        Retrieve language usage for a project.

        Args:
            project_id (str): GitLab project ID or namespace path.

        Returns:
            dict[str, float]: Mapping of language to percentage.
        """
        url = f"{self.BASE_URL}/projects/{project_id}/languages"
        return self.rate_limit_get(url)

    def get_contributors(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve contributor statistics for a project.

        Args:
            project_id (str): GitLab project identifier.

        Returns:
            list[dict]: List of contributor records.
        """
        url = f"{self.BASE_URL}/projects/{project_id}/repository/contributors"
        return self.rate_limit_get(url)

    def get_license(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve license information for a project.

        Args:
            project_id (str): GitLab project ID.

        Returns:
            dict | None: License spec or None if unavailable.
        """
        url = f"{self.BASE_URL}/projects/{project_id}/license"
        try:
            return self.rate_limit_get(url)
        except requests.HTTPError:
            return None

    def get_latest_release(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest release of a GitLab project.

        Args:
            project_id (str): Project identifier.

        Returns:
            dict | None: Latest release or None if no releases exist.
        """
        url = f"{self.BASE_URL}/projects/{project_id}/releases"
        try:
            releases = self.rate_limit_get(url)
            return releases[0] if releases else None
        except requests.HTTPError:
            return None

    def get_commits(self, project_id: str, per_page: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve commits for a project.

        Args:
            project_id (str): GitLab project ID.
            per_page (int): Number of commits to return.

        Returns:
            list[dict]: Commit records.
        """
        url = f"{self.BASE_URL}/projects/{project_id}/repository/commits?per_page={per_page}"
        return self.rate_limit_get(url)
