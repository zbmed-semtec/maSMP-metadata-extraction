"""
Base class for platform-specific Git repository clients (GitHub, GitLab, Codeberg, etc.).

Design principle: this class defines a *normalized* contract for repository
traversal (list a directory, fetch a file) and owns all platform-agnostic
logic built on top of that contract (recursive traversal, README/LICENSE/
CITATION/CHANGELOG discovery, citation parsing). Platform-specific API shapes
(GitHub's dual-purpose "contents" endpoint vs. GitLab's separate "tree"/"files"
endpoints, etc.) are implemented by subclasses behind `list_directory` and
`get_file`, and never leak into this class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import yaml

from app.layer_3.plugins.shared.caching_http_client import CachingHttpClient
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher

@dataclass
class RepositoryItem:
    """A normalized representation of a single file/directory entry in a repository tree."""
    name: str
    path: str
    is_dir: bool


class FileNotFoundOnPlatformError(Exception):
    """Raised when a requested file path does not exist / is not a file on the platform."""
    pass


class GitPlatformClient(CachingHttpClient, ABC):
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
        super().__init__(context, state)
        self._repository_owner: str | None = None
        self._repository_name: str | None = None
        self._parsed_citations: list[dict] | None = None
        self._dois_from_citation: set[str] | None = None
        self._dois_from_readme: set[str] | None = None
        self.headers = self._build_headers()

    # ------------------------------------------------------------------
    # Platform identity / API basics — must be implemented per platform
    # ------------------------------------------------------------------

    @abstractmethod
    def _get_api_base_url(self) -> str:
        """Returns the base URL for the platform's API."""
        pass

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

    # ------------------------------------------------------------------
    # Repository metadata — must be implemented per platform
    # ------------------------------------------------------------------

    @abstractmethod
    def get_repository(self) -> dict:
        """Fetches the repository metadata."""
        pass

    @abstractmethod
    def get_contributors(self) -> list:
        """Fetches the contributor activity data for the repository."""
        pass

    @abstractmethod
    def get_languages(self) -> dict:
        """Fetches the programming languages used in the repository."""
        pass

    @abstractmethod
    def get_releases(self) -> list:
        """Fetches the list of releases for the repository."""
        pass

    @abstractmethod
    def get_tags(self) -> list:
        """Fetches the list of tags for the repository."""
        pass

    @abstractmethod
    def get_default_branch(self) -> str:
        """Fetches the default branch name for the repository."""
        pass

    # ------------------------------------------------------------------
    # Normalized content contract — must be implemented per platform.
    #
    # These two methods are the *only* place platform-specific content-API
    # shape is allowed to live. Everything below this point is generic
    # traversal/discovery logic built purely on top of these two calls.
    # ------------------------------------------------------------------

    @abstractmethod
    def list_directory(self, path: str = "") -> list[RepositoryItem]:
        """Lists the immediate entries (files & directories) at the given path.

        Args:
            path: Directory path relative to the repo root. "" means repo root.

        Returns:
            A list of RepoEntry describing immediate children of `path`.

        Raises:
            FileNotFoundOnPlatformError: if `path` does not exist or is not a directory.
        """
        pass

    @abstractmethod
    def get_file(self, path: str, ref: str | None = None) -> dict:
        """Fetches a single file's metadata and content.

        Args:
            path: File path relative to the repo root.
            ref: Branch, tag, or commit SHA (defaults to the repository's default branch).

        Returns:
            A dict containing at least a "content" key with the file's decoded
            (UTF-8 text) content, when the file exists and is text-decodable.

        Raises:
            FileNotFoundOnPlatformError: if `path` does not exist or is not a file.
        """
        pass

    def get_raw_file(self, path: str) -> str:
        """Fetches the raw text content of a file at the given path in the repository."""
        return self.get_file(path).get("content", "")

    # ------------------------------------------------------------------
    # Generic traversal built on the normalized contract above
    # ------------------------------------------------------------------

    def list_contents(self, path: str = "", depth: int = 1) -> list[RepositoryItem]:
        """Recursively lists repository file/directory entries up to the given depth.

        Args:
            path: Directory path to start from ("" = repo root).
            depth: How many levels of subdirectories to recurse into.
                   depth=1 lists only the immediate contents of `path`.

        Returns:
            A flat list of RepoEntry for all discovered files/directories.
        """
        if depth <= 0:
            return []

        try:
            entries = self.list_directory(path)
        except FileNotFoundOnPlatformError:
            return []

        # Iterate over a stable copy; accumulate into a separate list so we
        # never mutate the collection we're iterating over.
        results: list[RepositoryItem] = list(entries)
        for entry in entries:
            if entry.is_dir:
                results.extend(self.list_contents(entry.path, depth - 1))
        return results

    def _discover_files_by_prefix(self, prefix: str) -> list[RepositoryItem]:
        """Helper method to discover files matching a given name prefix (case-insensitive)."""
        files = self.list_contents()
        return [f for f in files if not f.is_dir and f.name.lower().startswith(prefix)]

    def discover_readme_candidates(self) -> list[RepositoryItem]:
        """Finds files in the repository whose names suggest they are README files."""
        return self._discover_files_by_prefix("readme")

    def discover_license_candidates(self) -> list[RepositoryItem]:
        """Finds files in the repository whose names suggest they are license files."""
        return self._discover_files_by_prefix("license")

    def discover_citation_candidates(self) -> list[RepositoryItem]:
        """Finds files in the repository whose names suggest they are citation files."""
        return self._discover_files_by_prefix("citation")

    def discover_changelog_candidates(self) -> list[RepositoryItem]:
        """Finds files in the repository whose names suggest they are changelog files."""
        return self._discover_files_by_prefix("changelog")

    def get_multiple_files(self, paths: list[str]) -> list[dict]:
        """Fetches the content for multiple file paths, skipping files that can't be fetched."""
        files = []
        for path in paths:
            try:
                file = self.get_file(path)
            except FileNotFoundOnPlatformError:
                continue
            if "content" in file:
                files.append(file)
        return files

    def get_readme_candidate_files(self) -> list[dict]:
        """Fetches the content of all discovered README candidate files."""
        candidates = self.discover_readme_candidates()
        return self.get_multiple_files([c.path for c in candidates])

    def get_license_candidate_files(self) -> list[dict]:
        """Fetches the content of all discovered license candidate files."""
        candidates = self.discover_license_candidates()
        return self.get_multiple_files([c.path for c in candidates])

    def get_citation_candidate_files(self) -> list[dict]:
        """Fetches the content of all discovered citation candidate files."""
        candidates = self.discover_citation_candidates()
        return self.get_multiple_files([c.path for c in candidates])

    def get_changelog_candidate_files(self) -> list[dict]:
        """Fetches the content of all discovered changelog candidate files."""
        candidates = self.discover_changelog_candidates()
        return self.get_multiple_files([c.path for c in candidates])

    def get_parsed_citations(self) -> list[dict]:
        """Parses discovered citation files (e.g. CITATION.cff) as YAML, caching the result."""
        if self._parsed_citations is None:
            citation_files = self.get_citation_candidate_files()
            parsed = []
            for file in citation_files:
                content = file.get("content")
                if not content:
                    continue
                try:
                    cff_data = yaml.safe_load(content)
                except yaml.YAMLError:
                    continue
                if cff_data is not None:
                    parsed.append(cff_data)
            self._parsed_citations = parsed
        return self._parsed_citations
    
    def get_dois_from_readmes(self) -> list[str]:
        if self._dois_from_readme is None:
            result = set()
            readmes = self.get_readme_candidate_files()
            for readme in readmes:
                readme_content = readme.get("content")
                if readme_content:
                    doi_candidates = URLPatternMatcher.check_zenodo_badge(readme_content)
                    for doi_url in doi_candidates:
                        result.add(doi_url)
            self._dois_from_readme = result
        return self._dois_from_readme
    
    def get_dois_from_parsed_citaitons(self) -> set[str]:
        if self._dois_from_citation is None:
            citations = self.get_parsed_citations()
            identifiers = set()
            for cff in citations:
                for cffIdentifier in cff.get("identifiers", []):
                    if cffIdentifier.get("type") == "doi" and cffIdentifier.get("value"):
                        doi_url = f"https://doi.org/{cffIdentifier['value']}"
                        identifiers.add(doi_url)
                doi = cff.get("doi")
                if doi:
                    doi_url = f"https://doi.org/{doi}"
                    identifiers.add(doi_url)
            self._dois_from_citation = identifiers
        return self._dois_from_citation