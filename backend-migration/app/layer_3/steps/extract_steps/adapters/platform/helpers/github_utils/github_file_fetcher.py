from __future__ import annotations
from typing import Optional

import requests


class GitHubFileFetcher:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.headers = {}
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"

    def fetch_file_content(self, url: str) -> Optional[str]:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException:
            pass
        return None

    def fetch_file_from_repo(self, owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[str]:
        return self.fetch_file_content(f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}")

    def list_repo_contents(self, owner: str, repo: str, path: str = "") -> Optional[list]:
        try:
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                timeout=10,
            )
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
