"""
Layer 3: Adapters - GitLab
GitLab file fetcher - fetches files from GitLab repositories
"""
import requests
import base64
from typing import Optional


class GitLabFileFetcher:
    """Fetches files from GitLab repositories"""

    def __init__(self, access_token: Optional[str] = None, base_url: str = "https://gitlab.com"):
        """
        Initialize file fetcher.

        Args:
            access_token: GitLab personal access token
            base_url: GitLab instance URL (default: gitlab.com)
        """
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        
        self.headers = {}
        if access_token:
            self.headers["PRIVATE-TOKEN"] = access_token

    def fetch_file_content(self, url: str) -> Optional[str]:
        """
        Fetch raw file content using a direct URL (GitLab raw links).

        Args:
            url: File raw URL
            
        Returns:
            File content or None
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException:
            pass
        return None

    def fetch_file_from_repo(self, owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[str]:
        """
        Fetch a file from a GitLab repository.
        Signature is identical to GitHub version.

        Args:
            owner: GitLab group/user name
            repo: Repository name
            file_path: Path within repo
            branch: Branch name

        Returns:
            Raw file content or None
        """
        project_path = f"{owner}/{repo}"
        encoded_project = requests.utils.quote(project_path, safe="")

        api_url = (
            f"{self.base_url}/api/v4/projects/{encoded_project}/repository/files/"
            f"{requests.utils.quote(file_path, safe='')}"
            f"?ref={branch}"
        )

        try:
            response = requests.get(api_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
        except requests.exceptions.RequestException:
            pass

        return None

    def list_repo_contents(self, owner: str, repo: str, path: str = "") -> Optional[list]:
        """
        List repository contents in a given path.
        Signature identical to GitHub version.

        Args:
            owner: GitLab group/user
            repo: repository name
            path: directory path inside repo

        Returns:
            List of file/directory info or None
        """

        project_path = f"{owner}/{repo}"
        encoded_project = requests.utils.quote(project_path, safe="")

        api_url = (
            f"{self.base_url}/api/v4/projects/{encoded_project}/repository/tree"
            f"?path={requests.utils.quote(path, safe='')}&per_page=100"
        )

        try:
            response = requests.get(api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass

        return None

    def is_file_reachable(self, url: str) -> bool:
        """
        Check if a raw GitLab file URL is reachable.
        Works the same as GitHub version.

        Args:
            url: Raw file URL

        Returns:
            True if reachable
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
