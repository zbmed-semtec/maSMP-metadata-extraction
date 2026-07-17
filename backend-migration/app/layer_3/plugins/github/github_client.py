from app.layer_3.plugins.platform_client import PlatformClient
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState

class GitHubClient(PlatformClient):
    """Client for interacting with the GitHub API,
    providing cached access to repository metadata, contents, and related resources."""

    def _get_api_base_url(self) -> str:
        """Returns the GitHub API base URL."""
        return "https://api.github.com"

    def _build_headers(self) -> dict:
        """Builds request headers for GitHub API."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "maSMP-metadata-extraction",
        }
        if self.context.access_token:
            headers["Authorization"] = f"token {self.context.access_token}"
        return headers

    def _extract_repository_info(self, context: ExtractionContext) -> tuple[str, str]:
        """Parses the repository owner and name from the context's repository URL.
        
        Handles GitHub URLs in formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - github.com/owner/repo
        """
        repository_url = context.repo_url.strip("/")
        
        # Remove .git suffix if present
        if repository_url.endswith(".git"):
            repository_url = repository_url[:-4]
        
        # Extract parts after domain
        parts = repository_url.split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL format. Expected: https://github.com/owner/repo")
        
        # Get last two parts (owner and repo)
        return parts[-2], parts[-1]

    def get_repository(self) -> dict:
        """Fetches the repository metadata from the GitHub API."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}"
        return self._caching_get(url).json()

    def get_contributors(self) -> list:
        """Fetches the list of contributors for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contributors"
        return self._caching_get(url).json()

    def get_stargazers_count(self) -> int:
        """Fetches the number of stars for the repository."""
        repository = self.get_repository()
        return repository.get("stargazers_count", 0)

    def get_forks_count(self) -> int:
        """Fetches the number of forks for the repository."""
        repository = self.get_repository()
        return repository.get("forks_count", 0)

    def get_watchers_count(self) -> int:
        """Fetches the number of watchers for the repository."""
        repository = self.get_repository()
        return repository.get("watchers_count", 0)

    def get_open_issues_count(self) -> int:
        """Fetches the number of open issues for the repository."""
        repository = self.get_repository()
        return repository.get("open_issues_count", 0)

    def get_pull_requests(self, state: str = "open") -> list:
        """Fetches pull requests for the repository.
        
        Args:
            state: Pull request state filter ('open', 'closed', or 'all')
        
        Returns:
            List of pull request objects
        """
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/pulls?state={state}"
        return self._caching_get(url).json()

    def get_issues(self, state: str = "open") -> list:
        """Fetches issues for the repository.
        
        Args:
            state: Issue state filter ('open', 'closed', or 'all')
        
        Returns:
            List of issue objects
        """
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/issues?state={state}"
        return self._caching_get(url).json()

    def get_commits(self, per_page: int = 30) -> list:
        """Fetches recent commits for the repository.
        
        Args:
            per_page: Number of commits to return per page
        
        Returns:
            List of commit objects
        """
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/commits?per_page={per_page}"
        return self._caching_get(url).json()

    def get_latest_commit(self) -> dict:
        """Fetches the latest commit for the repository."""
        commits = self.get_commits(per_page=1)
        return commits[0] if commits else {}

    def get_network_stats(self) -> dict:
        """Fetches network statistics for the repository."""
        repository = self.get_repository()
        return {
            "stargazers_count": repository.get("stargazers_count", 0),
            "forks_count": repository.get("forks_count", 0),
            "watchers_count": repository.get("watchers_count", 0),
            "open_issues_count": repository.get("open_issues_count", 0),
        }

    def get_branch(self, branch: str = "main") -> dict:
        """Fetches information about a specific branch.
        
        Args:
            branch: Branch name (defaults to 'main')
        
        Returns:
            Branch object with commit information
        """
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/branches/{branch}"
        return self._caching_get(url).json()

    def get_branches(self) -> list:
        """Fetches all branches for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/branches"
        return self._caching_get(url).json()

    def get_default_branch(self) -> str:
        """Fetches the default branch name for the repository."""
        repository = self.get_repository()
        return repository.get("default_branch", "main")

    def get_readme(self) -> dict:
        """Fetches the README file for the repository from GitHub's dedicated endpoint."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/readme"
        try:
            return self._caching_get(url).json()
        except Exception:
            # Fall back to discovering README candidates
            return self.get_readme_candidate_files()[0] if self.get_readme_candidate_files() else {}

    def get_license(self) -> dict:
        """Fetches the license information for the repository from GitHub's dedicated endpoint."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/license"
        try:
            return self._caching_get(url).json()
        except Exception:
            # Fall back to discovering license candidates
            return self.get_license_candidate_files()[0] if self.get_license_candidate_files() else {}

    def get_code_frequency(self) -> list:
        """Fetches the code frequency statistics for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/stats/code_frequency"
        try:
            return self._caching_get(url).json()
        except Exception:
            return []

    def get_commit_activity(self) -> list:
        """Fetches the commit activity statistics for the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/stats/commit_activity"
        try:
            return self._caching_get(url).json()
        except Exception:
            return []

    def search_repositories(self, query: str, per_page: int = 10) -> list:
        """Searches for repositories on GitHub.
        
        Args:
            query: Search query string
            per_page: Number of results per page
        
        Returns:
            List of repository objects matching the query
        """
        url = f"{self._get_api_base_url()}/search/repositories?q={query}&per_page={per_page}"
        response = self._caching_get(url).json()
        return response.get("items", [])

    def get_user(self, username: str) -> dict:
        """Fetches information about a GitHub user.
        
        Args:
            username: GitHub username
        
        Returns:
            User object with profile information
        """
        url = f"{self._get_api_base_url()}/users/{username}"
        return self._caching_get(url).json()

    def get_repository_owner_info(self) -> dict:
        """Fetches information about the repository owner."""
        return self.get_user(self.get_repository_owner())

    def is_repository_public(self) -> bool:
        """Checks if the repository is public."""
        repository = self.get_repository()
        return not repository.get("private", True)

    def get_repository_description(self) -> str:
        """Fetches the repository description."""
        repository = self.get_repository()
        return repository.get("description", "")

    def get_repository_homepage(self) -> str:
        """Fetches the repository homepage URL."""
        repository = self.get_repository()
        return repository.get("homepage", "")

    def get_created_at(self) -> str:
        """Fetches the repository creation date."""
        repository = self.get_repository()
        return repository.get("created_at", "")

    def get_updated_at(self) -> str:
        """Fetches the repository last update date."""
        repository = self.get_repository()
        return repository.get("updated_at", "")

    def get_pushed_at(self) -> str:
        """Fetches the repository last push date."""
        repository = self.get_repository()
        return repository.get("pushed_at", "")