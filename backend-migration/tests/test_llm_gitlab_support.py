"""Tests for platform-aware README LLM extraction."""
from __future__ import annotations

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.helpers import repository_files
from app.layer_3.steps.extract_steps.services.llm.extract_llm_property_step import (
    ExtractLlmPropertyStep,
    _normalize_people,
)
from app.layer_3.steps.extract_steps.services.llm.llm_extractor import LLMExtractor


class _Fetcher:
    def __init__(self, content: str):
        self.content = content
        self.calls: list[tuple[str, str, str, str]] = []

    def fetch_file_from_repo(self, owner: str, repo: str, name: str, branch: str) -> str:
        self.calls.append((owner, repo, name, branch))
        return self.content


def test_repository_file_content_uses_gitlab_fetcher(monkeypatch):
    fetcher = _Fetcher("# GitLab README")
    monkeypatch.setattr(repository_files, "gitlab_file_fetcher", lambda _context, _state: fetcher)
    monkeypatch.setattr(
        repository_files,
        "github_file_fetcher",
        lambda *_args: (_ for _ in ()).throw(AssertionError("GitHub fetcher must not be used")),
    )

    content = repository_files.repository_file_content(
        StepContext(
            repo_url="https://gitlab.com/group/project",
            domain="software",
            schema="maSMP",
            platform="gitlab",
        ),
        StepState(metadata=SoftwareMetadata()),
        "readme_content",
        ("README.md",),
    )

    assert content == "# GitLab README"
    assert fetcher.calls == [("group", "project", "README.md", "main")]


def test_llm_prompt_and_people_normalization_support_gitlab():
    prompt = ExtractLlmPropertyStep()._build_prompt(
        "contributors",
        "Maintainer: @alice",
        {"property_rules": {"default": "Use evidence."}},
        platform="gitlab",
        repo_url="https://gitlab.com/group/project",
    )

    assert "Source platform: gitlab." in prompt
    assert "GitHub and GitLab URLs" in prompt
    assert "platform-neutral `url`" in prompt
    assert _normalize_people([{"name": "Alice", "gitlab_url": "https://gitlab.com/alice"}]) == [
        {"@type": "Person", "name": "Alice", "familyName": "Alice", "url": "https://gitlab.com/alice"}
    ]


def test_llm_extractor_detects_gitlab_platform(monkeypatch):
    captured: dict[str, str | None] = {}

    def capture_run(_self, context, state):
        captured["platform"] = context.platform
        return state

    monkeypatch.setattr(ExtractLlmPropertyStep, "run", capture_run)

    LLMExtractor().extract_with_llm(SoftwareMetadata(), "https://gitlab.com/group/project")

    assert captured["platform"] == "gitlab"
