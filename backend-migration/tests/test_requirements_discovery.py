"""Unit tests for requirements file discovery helpers."""
from __future__ import annotations

from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils.requirements_discovery import (
    discover_requirement_urls_from_state,
)


def test_discovery_uses_html_url_from_api_listing():
    def _list_contents(owner: str, repo: str, path: str):
        if path == "":
            return [
                {
                    "type": "file",
                    "name": "pyproject.toml",
                    "path": "pyproject.toml",
                    "html_url": "https://github.com/org/repo/blob/develop/pyproject.toml",
                }
            ]
        return []

    reachable: list[str] = []

    def _is_reachable(url: str) -> bool:
        reachable.append(url)
        return url.endswith("/blob/develop/pyproject.toml")

    urls = discover_requirement_urls_from_state(
        state_data={
            "normalized_repo_url": "https://github.com/org/repo",
            "repo_payload": {"default_branch": "develop"},
            "list_contents_fn": _list_contents,
            "is_file_reachable_fn": _is_reachable,
        },
        platform="github",
        repo_url="https://github.com/org/repo",
    )

    assert urls == ["https://github.com/org/repo/blob/develop/pyproject.toml"]
    assert reachable == ["https://github.com/org/repo/blob/develop/pyproject.toml"]


def test_discovery_falls_back_to_root_probe_when_api_listing_fails():
    def _list_contents(owner: str, repo: str, path: str):
        return None

    def _is_reachable(url: str) -> bool:
        return url == "https://github.com/org/repo/blob/master/requirements.txt"

    urls = discover_requirement_urls_from_state(
        state_data={
            "normalized_repo_url": "https://github.com/org/repo",
            "repo_payload": {"default_branch": "master"},
            "list_contents_fn": _list_contents,
            "is_file_reachable_fn": _is_reachable,
        },
        platform="github",
        repo_url="https://github.com/org/repo",
    )

    assert urls == ["https://github.com/org/repo/blob/master/requirements.txt"]


def test_discovery_finds_requirements_dev_txt():
    def _list_contents(owner: str, repo: str, path: str):
        if path == "":
            return [{"type": "file", "name": "requirements-dev.txt", "path": "requirements-dev.txt"}]
        return []

    def _is_reachable(url: str) -> bool:
        return url.endswith("/blob/main/requirements-dev.txt")

    urls = discover_requirement_urls_from_state(
        state_data={
            "normalized_repo_url": "https://github.com/org/repo",
            "list_contents_fn": _list_contents,
            "is_file_reachable_fn": _is_reachable,
        },
        platform="github",
        repo_url="https://github.com/org/repo.git",
    )

    assert urls[0].endswith("/blob/main/requirements-dev.txt")


def test_gitlab_discovery_checks_root_once_without_follow_up_requests():
    listed_paths: list[str] = []

    def _list_contents(owner: str, repo: str, path: str):
        listed_paths.append(path)
        return [
            {"type": "blob", "name": "pyproject.toml", "path": "pyproject.toml"},
            {"type": "tree", "name": "nested", "path": "nested"},
        ]

    def _is_reachable(_url: str) -> bool:
        raise AssertionError("GitLab listings must not trigger follow-up URL probes")

    urls = discover_requirement_urls_from_state(
        state_data={
            "normalized_repo_url": "https://gitlab.com/group/project",
            "repo_payload": {"default_branch": "develop"},
            "list_contents_fn": _list_contents,
            "is_file_reachable_fn": _is_reachable,
        },
        platform="gitlab",
        repo_url="https://gitlab.com/group/project",
    )

    assert listed_paths == [""]
    assert urls == ["https://gitlab.com/group/project/-/blob/develop/pyproject.toml"]
