import base64
from time import sleep
import requests
import yaml
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState

def fetchFunction(url: str, headers: dict = None) -> requests.Response:
    for trial in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            print("timeout for url: ", url)
            sleep(1)

class CodebergClient:
    def __init__(self, context: ExtractionContext, state: ExtractionState):
        self.base_url = "https://codeberg.org/api/v1"
        self.cache = {}
        self.context = context
        self.state = state
        self._repository_owner = None
        self._repository_name  = None
        self._parsed_citations = None
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "maSMP-metadata-extraction",
            "Authorization": f"token {self.context.access_token}" if self.context.access_token else None
        }

    def _extract_repository_info(self, context: ExtractionContext) -> tuple[str, str]:
        repository_url = context.repo_url
        parts = repository_url.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid repository URL format.")
        return parts[-2], parts[-1]

    def get_repository_owner(self) -> str:
        if self._repository_owner is None:
            self._repository_owner, self._repository_name = self._extract_repository_info(self.context)
        return self._repository_owner

    def get_repository_name(self) -> str:
        if self._repository_name is None:
            self._repository_owner, self._repository_name = self._extract_repository_info(self.context)
        return self._repository_name

    def _caching_get(self, url: str, fetch_function=fetchFunction) -> dict:
        if url not in self.cache:
            self.cache[url] = fetch_function(url, headers=self.headers)
        return self.cache[url]

    def get_repository(self) -> dict:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}"
        return self._caching_get(url).json()

    def get_contributors(self) -> list:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contributors"
        return self._caching_get(url).json()

    def get_languages(self) -> dict:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/languages"
        return self._caching_get(url).json()

    def get_releases(self) -> list:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/releases"
        return self._caching_get(url).json()
    
    def get_tags(self) -> list:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/tags"
        return self._caching_get(url).json()

    def get_tags(self) -> list:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/tags"
        return self._caching_get(url).json()

    def get_topics(self) -> dict:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/topics"
        return self._caching_get(url).json()

    def get_raw_file(self, path: str) -> str:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/raw/{path}"
        return self._caching_get(url).text

    def get_content_encoded(self, path: str = "") -> dict:
        url = f"{self.base_url}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contents/{path}"
        return self._caching_get(url).json()
    
    def get_content(self, path: str = "") -> dict:
        raw = self.get_content_encoded(path)
        if "encoding" in raw and raw["encoding"] == "base64":
            raw["content"] = base64.b64decode(raw["content"]).decode("utf-8")
        return raw
    
    def list_contents(self, path: str = "", depth=1) -> list:
        if depth <= 0:
            return []
        content = self.get_content(path)
        for item in content:
            if item["type"] == "dir":
                content.extend(self.list_contents(item["path"], depth - 1))
        return content
    
    def discover_readme_candidates(self) -> list:
        files = self.list_contents()
        readme_candidates = [f for f in files if f["type"] == "file" and f["name"].lower().startswith("readme")]
        return readme_candidates

    def get_multiple_files(self, paths: list[str]) -> list[dict]:
        files = []
        for path in paths:
            file = self.get_content(path)
            if "content" in file:
                files.append(file)
        return files

    def get_readme_candidate_files(self) -> list:
        candidates = self.discover_readme_candidates()
        return self.get_multiple_files([candidate["path"] for candidate in candidates])
    
    def discover_citation_candidates(self) -> list:
        files = self.list_contents()
        citation_candidates = [f for f in files if f["type"] == "file" and f["name"].lower().startswith("citation")]
        return citation_candidates
    
    def get_citation_candidate_files(self) -> list:
        candidates = self.discover_citation_candidates()
        return self.get_multiple_files([candidate["path"] for candidate in candidates])

    def get_parsed_citations(self) -> list[dict]:
        if self._parsed_citations is None:
            citation_files = self.get_citation_candidate_files()
            _parsed_citations = []
            for file in citation_files:
                if "content" in file:
                    try:
                        cff_data = yaml.safe_load(file["content"])
                        _parsed_citations.append(cff_data)
                    except yaml.YAMLError:
                        continue
            self._parsed_citations = _parsed_citations
        return self._parsed_citations