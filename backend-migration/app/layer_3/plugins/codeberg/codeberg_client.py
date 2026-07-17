from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_client import PlatformClient

class CodebergClient(PlatformClient):
    """Client for interacting with the Codeberg API and web endpoints,
    providing cached access to repository metadata, contents, and related resources."""

    def _get_api_base_url(self) -> str:
        """Returns the Codeberg API base URL."""
        return "https://codeberg.org/api/v1"

    def _build_headers(self) -> dict:
        """Builds request headers for Codeberg API."""
        return {
            "Accept": "application/vnd.github.v3+json",
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