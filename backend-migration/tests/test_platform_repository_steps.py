"""Unit tests for platform repository core-field extract steps."""
from __future__ import annotations

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_repository_property_steps import (
    github_basic_info_steps,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_repository_property_steps import (
    gitlab_basic_info_steps,
)


def test_extract_github_repository_property_steps_set_fields_and_records():
    calls: list[str] = []

    def _record(field: str) -> None:
        calls.append(field)

    state = StepState(
        metadata=SoftwareMetadata(),
        data={
            "repo_payload": {
                "name": "demo",
                "description": "Demo repository",
                "html_url": "https://github.com/org/repo",
            },
            "record_field": _record,
        },
    )
    context = StepContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="maSMP",
        platform="github",
    )

    for step in github_basic_info_steps():
        step.run(context, state)

    assert state.metadata.name == "demo"
    assert state.metadata.description == "Demo repository"
    assert str(state.metadata.url) == "https://github.com/org/repo"
    assert state.metadata.codeRepository == "https://github.com/org/repo.git"
    assert set(calls) == {"name", "description", "url", "codeRepository"}


def test_extract_gitlab_repository_property_steps_set_fields_and_records():
    calls: list[str] = []

    def _record(field: str) -> None:
        calls.append(field)

    state = StepState(
        metadata=SoftwareMetadata(),
        data={
            "repo_payload": {
                "name": "demo-gl",
                "description": "Demo GitLab repository",
                "web_url": "https://gitlab.com/org/repo",
                "http_url_to_repo": "https://gitlab.com/org/repo.git",
            },
            "record_field": _record,
        },
    )
    context = StepContext(
        repo_url="https://gitlab.com/org/repo",
        domain="software",
        schema="codemeta",
        platform="gitlab",
    )

    for step in gitlab_basic_info_steps():
        step.run(context, state)

    assert state.metadata.name == "demo-gl"
    assert state.metadata.description == "Demo GitLab repository"
    assert str(state.metadata.url) == "https://gitlab.com/org/repo"
    assert state.metadata.codeRepository == "https://gitlab.com/org/repo.git"
    assert set(calls) == {"name", "description", "url", "codeRepository"}
