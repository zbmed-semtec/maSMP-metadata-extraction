import base64

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.shared.git_platform_client import (
    GitPlatformClient,
    RepositoryItem,
    RepositoryFile,
    FileNotFoundOnPlatformError,
)


class CodbergRepositoryItem(RepositoryItem):
    @property
    def name(self) -> str:
        return self._raw["name"]

    @property
    def path(self) -> str:
        return self._raw["path"]

    @property
    def is_dir(self) -> bool:
        return self._raw["type"] == "dir"


class CodbergRepositoryFile(CodbergRepositoryItem, RepositoryFile):
    def get_content(self) -> str | None:
        raw_content = self._raw.get("content")
        if raw_content is None:
            return None
        if self._raw.get("encoding") == "base64":
            try:
                return base64.b64decode(raw_content).decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                return None
        return raw_content

    def get_html_url(self, _client):
        return self._raw.get('html_url')

class CodebergClient(GitPlatformClient):
    """Client for interacting with the Codeberg API and web endpoints,
    providing cached access to repository metadata, contents, and related resources."""

    def _get_api_base_url(self) -> str:
        """Returns the Codeberg API base URL."""
        return "https://codeberg.org/api/v1"

    def _build_headers(self) -> dict:
        """Builds request headers for Codeberg API."""
        return {
            "Accept": "application/vnd.Codberg.v3+json",
            "User-Agent": "maSMP-metadata-extraction",
            "Authorization": f"token {self.context.access_token}" if self.context.access_token else None
        }

    def _extract_repository_info(self, context: ExtractionContext) -> tuple[str, str]:
        """Parses the repository owner and name from the context's repository URL."""
        repository_url = context.repo_url
        parts = repository_url.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid repository URL format.")
        return parts[-2], parts[-1]

    def get_repository(self) -> dict:
        """Fetches the repository metadata from the Codeberg API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}"
        return self._caching_get(url).json()

    def get_contributors(self) -> list:
        """Fetches the contributor activity data for the repository."""
        url = f'https://codeberg.org/{self.get_repository_owner()}/{self.get_repository_name()}/activity/contributors/data'
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

    def get_clone_url(self):
        repository = self.get_repository()
        return repository.get("clone_url")

    def get_download_url(self):
        return f"https://codeberg.org/{self.get_repository_owner()}/{self.get_repository_name()}/archive/{self.get_default_branch()}.zip"

    def list_directory(self, path: str = "") -> list[RepositoryItem]:
        """Lists the immediate entries at `path` via Codeberg's (Gitea-compatible) contents API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contents/{path}"
        response = self._caching_get(url)
        if response.status_code == 404:
            raise FileNotFoundOnPlatformError(path)
        raw = response.json()
        if not isinstance(raw, list):
            raise FileNotFoundOnPlatformError(path)
        return [CodbergRepositoryItem(entry) for entry in raw]

    def _fetch_file(self, path: str, ref: str | None = None) -> RepositoryFile:
        """Fetches a single file's metadata and content via GitHub's contents API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contents/{path}"
        params = {"ref": ref} if ref else None
        response = self._caching_get(url, params=params)
        if response.status_code == 404:
            raise FileNotFoundOnPlatformError(path)
        raw = response.json()
        if isinstance(raw, list):
            raise FileNotFoundOnPlatformError(path)
        return CodbergRepositoryFile(raw)