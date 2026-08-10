"""Tests for platform profile pipelines replacing legacy extractor wrappers."""

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_1.provenance.software.defaults import SOURCE_GITHUB_API, SOURCE_GITLAB_API
from app.layer_3.composers.profiles.software_github_codemeta import (
    build_software_github_codemeta_pipeline,
)
from app.layer_3.composers.profiles.software_gitlab_codemeta import (
    build_software_gitlab_codemeta_pipeline,
)
from app.layer_3.extraction_metadata import InMemoryExtractionMetadataCollector
from app.layer_3.steps.contracts import ExtractionPipelineRunner, ExtractionContext, ExtractionState


def _run_pipeline(pipeline, repo_url: str, platform: str):
    collector = InMemoryExtractionMetadataCollector()
    default_source = SOURCE_GITHUB_API if platform == "github" else SOURCE_GITLAB_API

    def record(field: str, *, source=None, confidence=None) -> None:
        collector.record(
            field,
            source if source is not None else default_source,
            confidence if confidence is not None else 1.0,
        )

    state = ExtractionState(
        metadata=SoftwareMetadata(),
        data={
            "record_field": record,
            "repo_payload": {
                "name": "somef",
                "description": "Test repo",
                "html_url": "https://github.com/owner/repo",
                "web_url": "https://gitlab.com/owner/repo",
                "http_url_to_repo": "https://gitlab.com/owner/repo.git",
                "created_at": "2021-01-02T03:04:05Z",
                "updated_at": "2021-01-03T03:04:05Z",
                "last_activity_at": "2021-01-03T03:04:05Z",
                "pushed_at": "2021-01-04T03:04:05Z",
                "visibility": "public",
                "private": False,
                "has_discussions": True,
                "operations_access_level": "enabled",
                "archive_url": "https://api.github.com/repos/owner/repo/{archive_format}{/ref}",
                "topics": ["codemeta", "metadata"],
                "tag_list": ["gitlab", "metadata"],
            },
            "languages_payload": {"Python": 1000},
            "contributors_payload": [{"html_url": "https://github.com/dummy", "name": "Dummy User"}],
            "license_payload": {"license": {"name": "MIT", "url": "https://example.com/mit"}},
            "release_payload": {"tag_name": "v1.0.0", "published_at": "2021-02-01T00:00:00Z"},
            "commits_payload": [{"commit": {"committer": {"date": "2021-01-31T00:00:00Z"}}}],
            "readme_content": "",
            "cff_content": "",
            "license_content": "",
            "extracted_wayback_archive_url": None,
            "extracted_software_heritage_archive_url": None,
            "is_file_reachable_fn": lambda _url: True,
            "list_contents_fn": lambda _owner, _repo, _path="": [],
        },
    )
    context = ExtractionContext(repo_url=repo_url, domain="software", schema="CODEMETA", platform=platform)
    return ExtractionPipelineRunner().run(pipeline, context, state).metadata, collector.get_all()


def test_github_profile_populates_core_platform_fields():
    metadata, extraction_metadata = _run_pipeline(
        build_software_github_codemeta_pipeline(),
        "https://github.com/owner/repo",
        "github",
    )

    assert metadata.name == "somef"
    assert metadata.conditionsOfAccess == "Public"
    assert str(metadata.downloadUrl) == "https://api.github.com/repos/owner/repo/zipball/master"
    assert metadata.hasSourceCode == "https://github.com/owner/repo#id"
    assert metadata.programmingLanguage == ["Python"]
    assert metadata.softwareVersion == "v1.0.0"
    assert metadata.has_release is True
    assert extraction_metadata["name"]["source"] == SOURCE_GITHUB_API


def test_gitlab_profile_populates_core_platform_fields():
    metadata, extraction_metadata = _run_pipeline(
        build_software_gitlab_codemeta_pipeline(),
        "https://gitlab.com/owner/repo",
        "gitlab",
    )

    assert metadata.name == "somef"
    assert metadata.conditionsOfAccess == "Public"
    assert str(metadata.downloadUrl) == "https://gitlab.com/owner/repo/-/archive/master/somef-master.zip"
    assert metadata.hasSourceCode == "https://gitlab.com/owner/repo"
    assert metadata.programmingLanguage == ["Python"]
    assert metadata.softwareVersion == "v1.0.0"
    assert metadata.has_release is True
    assert extraction_metadata["name"]["source"] == SOURCE_GITLAB_API

