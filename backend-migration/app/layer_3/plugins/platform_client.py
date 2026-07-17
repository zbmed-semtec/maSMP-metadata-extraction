from abc import ABC, abstractmethod
from time import sleep
import requests
import yaml
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState


def fetchFunction(url: str, headers: dict = None, retries=3) -> requests.Response:
    """Performs a GET request with up to 3 retries on read timeout."""
    for trial in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            print("timeout for url: ", url)
        sleep(1)

class PlatformClient(ABC):
    """Abstract base class for platform-specific Git repository clients.
    
    Provides a common interface for interacting with different Git hosting platforms
    (Codeberg, GitHub, GitLab, etc.), handling repository metadata, contents, and resources.
    """

    def __init__(self, context: ExtractionContext, state: ExtractionState):
        """Initializes the client with extraction context/state and sets up request headers.
        
        Args:
            context: Extraction context containing repository URL and access token
            state: Extraction state for tracking extraction progress
        """
        self.context = context
        self.state = state
        self.cache = {}
        self._repository_owner = None
        self._repository_name = None
        self._parsed_citations = None
        self.headers = self._build_headers()

    @abstractmethod
    def _build_headers(self) -> dict:
        """Builds request headers specific to the platform's API requirements."""
        pass

    @abstractmethod
    def _extract_repository_info(self, context: ExtractionContext) -> tuple[str, str]:
        """Parses the repository owner and name from the context's repository URL.
        
        Returns:
            A tuple of (owner, repository_name)
        """
        pass

    @abstractmethod
    def _get_api_base_url(self) -> str:
        """Returns the base URL for the platform's API."""
        pass

    def get_repository_owner(self) -> str:
        """Returns the repository owner, extracting and caching it if not already set."""
        if self._repository_owner is None:
            self._repository_owner, self._repository_name = self._extract_repository_info(self.context)
        return self._repository_owner

    def get_repository_name(self) -> str:
        """Returns the repository name, extracting and caching it if not already set."""
        if self._repository_name is None:
            self._repository_owner, self._repository_name = self._extract_repository_info(self.context)
        return self._repository_name

    def _caching_get(self, url: str, fetch_function=fetchFunction) -> dict:
        """Fetches a URL using the given fetch function, caching the response for reuse."""
        if url not in self.cache:
            self.cache[url] = fetch_function(url, headers=self.headers)
        return self.cache[url]

    @abstractmethod
    def get_repository(self) -> dict:
        """Fetches the repository metadata."""
        pass

    @abstractmethod
    def get_contributors(self) -> list:
        """Fetches the contributor activity data for the repository."""
        pass

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

    def get_topics(self) -> dict:
        """Fetches the topics associated with the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/topics"
        return self._caching_get(url).json()

    def get_raw_file(self, path: str) -> str:
        """Fetches the raw text content of a file at the given path in the repository."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/raw/{path}"
        return self._caching_get(url).text

    def get_content_encoded(self, path: str = "") -> dict:
        """Fetches the raw (possibly base64-encoded) content listing/metadata for a given path."""
        url = f"{self._get_api_base_url()}/repos/{self.get_repository_owner()}/{self.get_repository_name()}/contents/{path}"
        return self._caching_get(url).json()

    def get_content(self, path: str = "") -> dict:
        """Fetches content for a path and decodes it if base64-encoded."""
        import base64
        raw = self.get_content_encoded(path)
        if "encoding" in raw and raw["encoding"] == "base64":
            raw["content"] = base64.b64decode(raw["content"]).decode("utf-8")
        return raw

    def list_contents(self, path: str = "", depth=1) -> list:
        """Recursively lists repository file/directory entries up to the given depth."""
        if depth <= 0:
            return []
        content = self.get_content(path)
        for item in content:
            if item["type"] == "dir" and "path" in item:
                content.extend(self.list_contents(item["path"], depth - 1))
        return content

    def _discover_files_by_prefix(self, prefix: str) -> list:
        """Helper method to discover files matching a given prefix."""
        files = self.list_contents()
        return [f for f in files if f["type"] == "file" and f["name"].lower().startswith(prefix)]

    def discover_readme_candidates(self) -> list:
        """Finds files in the repository whose names suggest they are README files."""
        return self._discover_files_by_prefix("readme")

    def discover_license_candidates(self) -> list:
        """Finds files in the repository whose names suggest they are license files."""
        return self._discover_files_by_prefix("license")

    def discover_citation_candidates(self) -> list:
        """Finds files in the repository whose names suggest they are citation files."""
        return self._discover_files_by_prefix("citation")

    def get_multiple_files(self, paths: list[str]) -> list[dict]:
        """Fetches the content for multiple file paths, skipping files with no content."""
        files = []
        for path in paths:
            file = self.get_content(path)
            if "content" in file:
                files.append(file)
        return files

    def get_readme_candidate_files(self) -> list:
        """Fetches the content of all discovered README candidate files."""
        candidates = self.discover_readme_candidates()
        return self.get_multiple_files([candidate["path"] for candidate in candidates])

    def get_license_candidate_files(self) -> list:
        """Fetches the content of all discovered license candidate files."""
        candidates = self.discover_license_candidates()
        return self.get_multiple_files([candidate["path"] for candidate in candidates])

    def get_citation_candidate_files(self) -> list:
        """Fetches the content of all discovered citation candidate files."""
        candidates = self.discover_citation_candidates()
        return self.get_multiple_files([candidate["path"] for candidate in candidates])

    def get_parsed_citations(self) -> list[dict]:
        """Parses discovered citation files (e.g. CITATION.cff) as YAML, caching the result."""
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