"""
Adapter-level tests for GitHubExtractor.
Verify that key fields and source recordings are populated correctly.
"""
from typing import Any, Dict, List

from app.adapters.github.github_extractor import GitHubExtractor
from app.domain.extraction_sources import SOURCE_GITHUB_API
from app.core.entities.repository_metadata import RepositoryMetadata


class DummyCollector:
    """Simple in-memory collector to capture record() calls from extractors."""

    def __init__(self) -> None:
        self.calls: List[tuple[str, str]] = []

    def record(self, entity_field: str, source: str, confidence: float) -> None:  # type: ignore[override]
        self.calls.append((entity_field, source))


class DummyGitHubClient:
    """Stub GitHub client returning fixed data for testing."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        return {
            "name": "somef",
            "description": "Test repo",
            "html_url": f"https://github.com/{owner}/{repo}",
            "created_at": "2020-01-02T03:04:05Z",
            "updated_at": "2020-01-03T03:04:05Z",
            "pushed_at": "2020-01-04T03:04:05Z",
            "private": False,
            "has_discussions": True,
            "archive_url": "https://api.github.com/repos/owner/repo/{archive_format}{/ref}",
            "topics": ["codemeta", "metadata"],
        }

    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        return {"Python": 12345, "Jupyter Notebook": 6789}

    def get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        return [{"html_url": "https://github.com/dummy"}]

    def get_license(self, owner: str, repo: str) -> Dict[str, Any]:
        return {"license": {"name": "MIT License", "url": "https://api.github.com/licenses/mit"}}

    def get_latest_release(self, owner: str, repo: str) -> Dict[str, Any]:
        return {"tag_name": "v1.0.0", "published_at": "2020-02-01T00:00:00Z"}

    def get_commits(self, owner: str, repo: str, per_page: int = 1) -> List[Dict[str, Any]]:
        return [{"commit": {"committer": {"date": "2020-01-31T00:00:00Z"}}}]


class DummyGitHubFileFetcher:
    """Stub file fetcher that treats all probed URLs as reachable."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token

    def is_file_reachable(self, url: str) -> bool:
        return True


def test_github_extractor_populates_core_fields(monkeypatch):
    """GitHubExtractor should populate key fields and record them with SOURCE_GITHUB_API."""
    extractor = GitHubExtractor(access_token=None)

    # Patch underlying client and file fetcher with our stubs
    extractor.client = DummyGitHubClient()
    extractor.file_fetcher = DummyGitHubFileFetcher()

    collector = DummyCollector()
    repo_url = "https://github.com/owner/repo"

    metadata: RepositoryMetadata = extractor.extract_platform_metadata(
        repo_url=repo_url,
        access_token=None,
        extraction_metadata=collector,  # type: ignore[arg-type]
    )

    # Verify key fields
    assert metadata.name == "somef"
    assert metadata.description == "Test repo"
    assert str(metadata.url) == "https://github.com/owner/repo"
    assert metadata.codeRepository == "https://github.com/owner/repo.git"
    assert metadata.dateCreated == "2020-01-02"
    assert metadata.dateModified == "2020-01-03"
    assert metadata.datePublished == "2020-01-04"
    assert metadata.conditionsOfAccess == "Public"
    assert metadata.isAccessibleForFree == "True"
    assert str(metadata.downloadUrl) == "https://api.github.com/repos/owner/repo/zipball/master"
    assert metadata.hasSourceCode == "https://github.com/owner/repo#id"
    assert metadata.codemeta_hasSourceCode == "https://github.com/owner/repo#id"
    assert metadata.keywords and set(metadata.keywords) == {"codemeta", "metadata"}
    assert metadata.programmingLanguage and set(metadata.programmingLanguage) == {
        "Python",
        "Jupyter Notebook",
    }
    assert metadata.contributor and metadata.contributor[0]["url"] == "https://github.com/dummy"
    assert metadata.license and metadata.license.name == "MIT License"
    assert metadata.softwareVersion == "v1.0.0"
    assert metadata.version == "v1.0.0"
    assert metadata.has_release is True
    assert metadata.codemeta_readme == "https://github.com/owner/repo/blob/main/README.md"
    assert metadata.masmp_changelog == "https://github.com/owner/repo/blob/main/CHANGELOG.md"

    # Verify recordings
    recorded_fields = {field for (field, source) in collector.calls if source == SOURCE_GITHUB_API}
    for expected in [
        "name",
        "description",
        "url",
        "codeRepository",
        "dateCreated",
        "dateModified",
        "datePublished",
        "conditionsOfAccess",
        "isAccessibleForFree",
        "issueTracker",
        "codemeta_issueTracker",
        "discussionUrl",
        "downloadUrl",
        "hasSourceCode",
        "codemeta_hasSourceCode",
        "keywords",
        "masmp_versionControlSystem",
        "programmingLanguage",
        "contributor",
        "license",
        "codemeta_readme",
        "masmp_changelog",
        "softwareVersion",
        "version",
    ]:
        assert expected in recorded_fields

