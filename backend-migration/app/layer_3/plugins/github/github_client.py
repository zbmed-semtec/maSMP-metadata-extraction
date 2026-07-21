"""
GitHub implementation of GitPlatformClient.

GitHub's `contents` endpoint already unifies file/directory access (unlike
GitLab's split tree/files endpoints), so `list_directory` and `get_file`
both hit the same endpoint here — mirroring the original Codeberg-style
implementation almost exactly, since Codeberg's API is Gitea's
GitHub-compatible surface.
"""

import base64

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.shared.git_platform_client import (
    GitPlatformClient,
    RepositoryItem,
    FileNotFoundOnPlatformError,
)


class GitHubClient(GitPlatformClient):
    """Client for interacting with the GitHub API,
    providing cached access to repository metadata, contents, and related resources."""

    def _get_api_base_url(self) -> str:
        """Returns the GitHub API base URL."""
        return "https://api.github.com"

    def _build_headers(self) -> dict:
        """Builds request headers for the GitHub API."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "maSMP-metadata-extraction",
        }
        if self.context.access_token:
            headers["Authorization"] = f"token {self.context.access_token}"
        return headers

    def _extract_repository_info(self, context: ExtractionContext) -> tuple[str, str]:
        """Parses the repository owner and name from the context's repository URL."""
        repository_url = context.repo_url
        parts = repository_url.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid repository URL format.")
        return parts[-2], parts[-1]

    def get_repository(self) -> dict:
        """Fetches the repository metadata from the GitHub API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}"
        return self._caching_get(url).json()

    def get_contributors(self) -> list:
        """Fetches the contributor list for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contributors"
        return self._caching_get(url).json()

    def get_languages(self) -> dict:
        """Fetches the programming languages used in the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/languages"
        return self._caching_get(url).json()

    def get_releases(self) -> list:
        """Fetches the list of releases for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/releases"
        return self._caching_get(url).json()

    def get_tags(self) -> list:
        """Fetches the list of tags for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/tags"
        return self._caching_get(url).json()

    def get_default_branch(self) -> str:
        """Fetches the default branch name for the repository."""
        repository = self.get_repository()
        return repository.get("default_branch", "main")

    def list_directory(self, path: str = "") -> list[RepositoryItem]:
        """Lists the immediate entries at `path` via GitHub's contents API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contents/{path}"
        response = self._caching_get(url)
        if response.status_code == 404:
            raise FileNotFoundOnPlatformError(path)
        raw = response.json()
        if not isinstance(raw, list):
            raise FileNotFoundOnPlatformError(path)
        return [
            RepositoryItem(name=e["name"], path=e["path"], is_dir=e["type"] == "dir")
            for e in raw
        ]

    def get_file(self, path: str, ref: str = None) -> dict:
        """Fetches a single file's metadata and decoded content via GitHub's contents API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contents/{path}"
        params = {"ref": ref} if ref else None
        response = self._caching_get(url, params=params)
        if response.status_code == 404:
            raise FileNotFoundOnPlatformError(path)
        raw = response.json()
        if isinstance(raw, list):
            raise FileNotFoundOnPlatformError(path)
        if raw.get("encoding") == "base64" and "content" in raw:
            raw["content"] = base64.b64decode(raw["content"]).decode("utf-8")
        return raw