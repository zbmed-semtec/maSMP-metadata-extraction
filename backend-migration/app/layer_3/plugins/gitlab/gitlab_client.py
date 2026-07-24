"""
GitLab implementation of GitPlatformClient.

Implements the normalized content contract (`list_directory` / `get_file`)
on top of GitLab's actual API shape:
- Directory listings go through the `repository/tree` endpoint.
- File content goes through the `repository/files/{path}` endpoint.
These are genuinely different endpoints on GitLab (unlike GitHub's unified
"contents" endpoint), so no shape-sniffing or unified method is attempted.
"""

import base64
from urllib.parse import quote

import requests

from app.layer_3.plugins.shared.git_platform_client import (
    GitPlatformClient,
    RepositoryItem,
    RepositoryFile,
    FileNotFoundOnPlatformError,
)
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState

class GitLabRepositoryItem(RepositoryItem):
    @property
    def name(self) -> str:
        return self._raw["name"]

    @property
    def path(self) -> str:
        return self._raw["path"]

    @property
    def is_dir(self) -> bool:
        return self._raw["type"] == "tree"

class GitLabRepositoryFile(GitLabRepositoryItem, RepositoryFile):
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

    def get_html_url(self):
        return self._raw.get("web_url")

class GitLabClient(GitPlatformClient):
    """Client for interacting with the GitLab API,
    providing cached access to repository metadata, contents, and related resources."""

    # ------------------------------------------------------------------
    # Platform identity / API basics
    # ------------------------------------------------------------------

    def _get_api_base_url(self) -> str:
        """Returns the GitLab API base URL."""
        return "https://gitlab.com/api/v4"

    def _build_headers(self) -> dict:
        """Builds request headers for GitLab API."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "maSMP-metadata-extraction",
        }
        if self.context.access_token:
            headers["Authorization"] = f"Bearer {self.context.access_token}"
        return headers

    def _extract_repository_info(self, context: ExtractionContext) -> tuple[str, str]:
        """Parses the repository namespace and name from the context's repository URL.

        Handles GitLab URLs in formats:
        - https://gitlab.com/namespace/project
        - https://gitlab.com/namespace/subgroup/project
        - https://gitlab.com/namespace/project.git
        - gitlab.com/namespace/project
        """
        repository_url = context.repo_url.strip("/")

        if repository_url.endswith(".git"):
            repository_url = repository_url[:-4]

        for prefix in ("https://", "http://"):
            if repository_url.startswith(prefix):
                repository_url = repository_url[len(prefix):]
                break
        if repository_url.startswith("gitlab.com/"):
            repository_url = repository_url[len("gitlab.com/"):]

        parts = repository_url.split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitLab repository URL format. Expected: https://gitlab.com/namespace/project")

        owner = "/".join(parts[:-1])
        name = parts[-1]
        return owner, name

    def get_project_id(self) -> str:
        """Returns the URL-encoded project path (namespace/project), used as GitLab's project identifier."""
        return quote(f"{self.get_repository_owner()}/{self.get_repository_name()}", safe="")

    # ------------------------------------------------------------------
    # Repository metadata
    # ------------------------------------------------------------------

    def get_repository(self) -> dict:
        """Fetches the project metadata from the GitLab API."""
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}"
        return self._caching_get(url).json()

    def get_contributors(self) -> list:
        """Fetches the list of contributors for the repository."""
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/contributors"
        return self._caching_get(url).json()

    def get_programming_languages(self) -> dict[str, float]:
        """Fetches the programming language breakdown for the project."""
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/languages"
        return self._caching_get(url).json()

    def get_languages(self) -> dict:
        """Fetches the programming languages used in the repository (GitLab override)."""
        return self.get_programming_languages()

    def get_releases(self) -> list:
        """Fetches the list of releases for the repository."""
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/releases"
        return self._caching_get(url).json()

    def get_tags(self) -> list:
        """Fetches the list of tags for the repository."""
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/tags"
        return self._caching_get(url).json()

    def get_default_branch(self) -> str:
        """Fetches the default branch name for the repository."""
        repository = self.get_repository()
        return repository.get("default_branch", "main")

    # ------------------------------------------------------------------
    # Normalized content contract
    # ------------------------------------------------------------------

    def list_directory(self, path: str = "") -> list[RepositoryItem]:
        """Lists the immediate entries at `path` via GitLab's repository tree API.

        Raises:
            FileNotFoundOnPlatformError: if `path` doesn't exist (404) or isn't a directory.
        """
        ref = self.get_default_branch()
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/tree"
        params = {"ref": ref}
        if path:
            params["path"] = path

        try:
            response = self._caching_get(url, params=params)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise FileNotFoundOnPlatformError(path) from e
            raise

        raw_entries = response.json()
        return [GitLabRepositoryFile(entry) for entry in raw_entries]

    def _fetch_file(self, path: str, ref: str | None = None) -> dict:
        """Fetches a single file's metadata and decoded content via GitLab's files API.

        Args:
            path: File path relative to the repository root.
            ref: Branch, tag, or commit SHA (defaults to the project's default branch).

        Raises:
            FileNotFoundOnPlatformError: if `path` doesn't exist or isn't a file.
        """
        ref = ref or self.get_default_branch()
        encoded_path = quote(path, safe="")
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/files/{encoded_path}"

        try:
            raw = self._caching_get(url, params={"ref": ref}).json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise FileNotFoundOnPlatformError(path) from e
            raise

        return GitLabRepositoryFile(raw)

    # ------------------------------------------------------------------
    # GitLab-specific extras (not part of the shared base-class contract)
    # ------------------------------------------------------------------

    def get_forks_count(self) -> int:
        """Fetches the number of forks for the repository."""
        repository = self.get_repository()
        return repository.get("forks_count", 0)

    def get_open_issues_count(self) -> int:
        """Fetches the number of open issues for the repository."""
        repository = self.get_repository()
        return repository.get("open_issues_count", 0)

    def get_merge_requests(self, state: str = "opened") -> list:
        """Fetches merge requests for the repository.

        Args:
            state: Merge request state filter ('opened', 'closed', 'locked', or 'merged')

        Returns:
            List of merge request objects
        """
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/merge_requests"
        return self._caching_get(url, params={"state": state}).json()

    def get_issues(self, state: str = "opened") -> list:
        """Fetches issues for the repository.

        Args:
            state: Issue state filter ('opened', 'closed', or 'all')

        Returns:
            List of issue objects
        """
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/issues"
        return self._caching_get(url, params={"state": state}).json()

    def get_commits(self, per_page: int = 30) -> list:
        """Fetches recent commits for the repository.

        Args:
            per_page: Number of commits to return per page

        Returns:
            List of commit objects
        """
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/commits"
        return self._caching_get(url, params={"per_page": per_page}).json()

    def get_latest_commit(self) -> dict:
        """Fetches the latest commit for the repository."""
        commits = self.get_commits(per_page=1)
        return commits[0] if commits else {}

    def get_network_stats(self) -> dict:
        """Fetches network-level statistics for the repository."""
        repository = self.get_repository()
        return {
            "forks_count": repository.get("forks_count", 0),
            "open_issues_count": repository.get("open_issues_count", 0),
        }

    def get_branch(self, branch: str = "main") -> dict:
        """Fetches information about a specific branch.

        Args:
            branch: Branch name (defaults to 'main')

        Returns:
            Branch object with commit information
        """
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/branches/{quote(branch, safe='')}"
        return self._caching_get(url).json()

    def get_branches(self) -> list:
        """Fetches all branches for the repository."""
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}/repository/branches"
        return self._caching_get(url).json()

    def get_readme(self) -> dict:
        """Fetches the README file for the repository.

        GitLab doesn't have a dedicated README endpoint like GitHub; the project
        metadata includes a `readme_url`, but content must be fetched via the
        repository files API. Falls back to discovering README candidates.
        """
        repository = self.get_repository()
        readme_path = repository.get("readme_url")
        if readme_path:
            # readme_url points to the blob view; extract the file path relative to repo root
            # e.g. https://gitlab.com/namespace/project/-/blob/main/README.md
            try:
                file_path = readme_path.split("/-/blob/")[1].split("/", 1)[1]
                return self.get_file(file_path)
            except (IndexError, FileNotFoundOnPlatformError):
                pass
        candidates = self.get_readme_candidate_files()
        return candidates[0] if candidates else {}

    def get_license(self) -> dict:
        """Fetches the license information for the repository.

        GitLab exposes a `license` object embedded in project metadata (requires
        the `license=true` query param), rather than a dedicated license endpoint
        like GitHub. Falls back to discovering license candidates.
        """
        url = f"{self._get_api_base_url()}/projects/{self.get_project_id()}"
        try:
            repository = self._caching_get(url, params={"license": "true"}).json()
            license_info = repository.get("license")
            if license_info:
                return license_info
        except requests.exceptions.RequestException:
            pass
        candidates = self.get_license_candidate_files()
        return candidates[0] if candidates else {}

    def search_projects(self, query: str, per_page: int = 10) -> list:
        """Searches for projects on GitLab.

        Args:
            query: Search query string
            per_page: Number of results per page

        Returns:
            List of project objects matching the query
        """
        url = f"{self._get_api_base_url()}/projects"
        return self._caching_get(url, params={"search": query, "per_page": per_page}).json()

    def get_user(self, username: str) -> dict:
        """Fetches information about a GitLab user.

        Args:
            username: GitLab username

        Returns:
            User object with profile information
        """
        url = f"{self._get_api_base_url()}/users"
        results = self._caching_get(url, params={"username": username}).json()
        return results[0] if results else {}

    def get_repository_owner_info(self) -> dict:
        """Fetches information about the repository's namespace owner.

        Note: GitLab namespaces can be users or groups; this attempts a user
        lookup first and falls back to the namespace info embedded in project metadata.
        """
        repository = self.get_repository()
        namespace = repository.get("namespace", {})
        if namespace.get("kind") == "user":
            return self.get_user(namespace.get("path", self.get_repository_owner()))
        return namespace

    def is_repository_public(self) -> bool:
        """Checks if the repository is public."""
        repository = self.get_repository()
        return repository.get("visibility") == "public"

    def get_repository_description(self) -> str:
        """Fetches the repository description."""
        repository = self.get_repository()
        return repository.get("description", "")

    def get_repository_homepage(self) -> str:
        """Fetches the repository homepage/web URL."""
        repository = self.get_repository()
        return repository.get("web_url", "")

    def get_created_at(self) -> str:
        """Fetches the repository creation date."""
        repository = self.get_repository()
        return repository.get("created_at", "")

    def get_updated_at(self) -> str:
        """Fetches the repository last update date."""
        repository = self.get_repository()
        return repository.get("last_activity_at", "")