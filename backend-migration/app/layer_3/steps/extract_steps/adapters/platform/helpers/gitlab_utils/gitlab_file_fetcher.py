import base64
from typing import Optional

import requests


class GitLabFileFetcher:
    def __init__(self, access_token: Optional[str] = None, base_url: str = "https://gitlab.com"):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.headers = {}
        if access_token:
            self.headers["PRIVATE-TOKEN"] = access_token

    def fetch_file_content(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException:
            pass
        return None

    def fetch_file_from_repo(self, owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[str]:
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
                return base64.b64decode(data["content"]).decode("utf-8")
        except requests.exceptions.RequestException:
            pass
        return None

    def list_repo_contents(self, owner: str, repo: str, path: str = "") -> Optional[list]:
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
        try:
            response = requests.get(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
