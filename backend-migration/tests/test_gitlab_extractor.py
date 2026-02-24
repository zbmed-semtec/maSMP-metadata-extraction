"""
Adapter-level tests for GitLabExtractor.
Verify that key fields and source recordings are populated correctly.
"""
from typing import Any, Dict, List

from app.adapters.gitlab.gitlab_extractor import GitLabExtractor
from app.domain.extraction_sources import SOURCE_GITLAB_API
from app.core.entities.repository_metadata import RepositoryMetadata


class DummyCollector:
    """Simple in-memory collector to capture record() calls from extractors."""

    def __init__(self) -> None:
        self.calls: List[tuple[str, str]] = []

    def record(self, entity_field: str, source: str, confidence: float) -> None:  # type: ignore[override]
        self.calls.append((entity_field, source))


class DummyGitLabClient:
    """Stub GitLab client returning fixed data for testing."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token

    def get_project(self, project_id: str) -> Dict[str, Any]:
        return {
            "name": "somef",
            "description": "GitLab test repo",
            "web_url": "https://gitlab.com/owner/repo",
            "http_url_to_repo": "https://gitlab.com/owner/repo.git",
            "created_at": "2021-01-02T03:04:05Z",
            "last_activity_at": "2021-01-03T03:04:05Z",
            "visibility": "public",
            "operations_access_level": "enabled",
            "tag_list": ["gitlab", "metadata"],
        }

    def get_commits(self, project_id: str, per_page: int = 1) -> List[Dict[str, Any]]:
        return [{"committed_date": "2021-01-04T00:00:00Z"}]

    def get_languages(self, project_id: str) -> Dict[str, int]:
        return {"Python": 1000, "Go": 500}

    def get_contributors(self, project_id: str) -> List[Dict[str, Any]]:
        return [{"name": "Dummy User", "email": "dummy@example.com"}]

    def get_license(self, project_id: str) -> Dict[str, Any]:
        return {"license": {"name": "Apache-2.0", "url": "https://gitlab.com/licenses/apache-2.0"}}

    def get_latest_release(self, project_id: str) -> Dict[str, Any]:
        return {"tag_name": "v2.0.0"}


class DummyGitLabFileFetcher:
    """Stub file fetcher that treats all probed URLs as reachable."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token

    def is_file_reachable(self, url: str) -> bool:
        return True


def test_gitlab_extractor_populates_core_fields(monkeypatch):
    """GitLabExtractor should populate key fields and record them with SOURCE_GITLAB_API."""
    extractor = GitLabExtractor(access_token=None)

    # Patch underlying client and file fetcher with our stubs
    extractor.client = DummyGitLabClient()
    extractor.file_fetcher = DummyGitLabFileFetcher()

    collector = DummyCollector()
    repo_url = "https://gitlab.com/owner/repo"

    metadata: RepositoryMetadata = extractor.extract_platform_metadata(
        repo_url=repo_url,
        access_token=None,
        extraction_metadata=collector,  # type: ignore[arg-type]
    )

    # Verify key fields
    assert metadata.name == "somef"
    assert metadata.description == "GitLab test repo"
    assert str(metadata.url) == "https://gitlab.com/owner/repo"
    assert metadata.codeRepository == "https://gitlab.com/owner/repo.git"
    assert metadata.dateCreated == "2021-01-02"
    assert metadata.dateModified == "2021-01-03"
    assert metadata.datePublished == "2021-01-04"
    assert metadata.conditionsOfAccess == "Public"
    assert metadata.isAccessibleForFree == "True"
    assert str(metadata.downloadUrl) == "https://gitlab.com/owner/repo/-/archive/master/somef-master.zip"
    assert str(metadata.issueTracker) == "https://gitlab.com/owner/repo/-/issues"
    assert str(metadata.codemeta_issueTracker) == "https://gitlab.com/owner/repo/-/issues"
    assert str(metadata.discussionUrl) == "https://gitlab.com/owner/repo/-/discussions"
    assert metadata.hasSourceCode == metadata.url
    assert metadata.codemeta_hasSourceCode == metadata.url
    assert metadata.keywords and set(metadata.keywords) == {"gitlab", "metadata"}
    assert metadata.programmingLanguage and set(metadata.programmingLanguage) == {"Python", "Go"}
    assert metadata.contributor and metadata.contributor[0]["name"] == "Dummy User"
    assert metadata.license and metadata.license.name == "Apache-2.0"
    assert metadata.softwareVersion == "v2.0.0"
    assert metadata.version == "v2.0.0"
    assert metadata.has_release is True
    assert metadata.codemeta_readme == "https://gitlab.com/owner/repo/-/blob/main/README.md"
    assert metadata.masmp_changelog == "https://gitlab.com/owner/repo/-/blob/main/CHANGELOG.md"

    # Verify recordings
    recorded_fields = {field for (field, source) in collector.calls if source == SOURCE_GITLAB_API}
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

