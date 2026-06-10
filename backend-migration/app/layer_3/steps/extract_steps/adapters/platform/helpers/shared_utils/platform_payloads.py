"""Lazy platform payload helpers for source-specific extraction steps."""

from urllib.parse import quote

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.github_utils.github_client import (
    GitHubClient,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.github_utils.github_file_fetcher import (
    GitHubFileFetcher,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.gitlab_utils.gitlab_client import (
    GitLabClient,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.gitlab_utils.gitlab_file_fetcher import (
    GitLabFileFetcher,
)
from app.layer_3.utils.url_pattern_matcher import URLPatternMatcher


def repo_parts(context: StepContext) -> tuple[str, str]:
    owner, repo = URLPatternMatcher.extract_repo_info(context.repo_url)
    return owner or "", repo or ""


def record_field(
    state: StepState,
    field: str,
    *,
    source: str | None = None,
    confidence: float | None = None,
) -> None:
    record = state.data.get("record_field")
    if callable(record):
        if source is not None:
            record(field, source=source, confidence=confidence)
        else:
            record(field)


def github_client(context: StepContext, state: StepState) -> GitHubClient:
    client = state.data.get("github_client")
    if client is None:
        client = GitHubClient(context.access_token)
        state.data["github_client"] = client
    return client


def github_file_fetcher(context: StepContext, state: StepState) -> GitHubFileFetcher:
    fetcher = state.data.get("github_file_fetcher")
    if fetcher is None:
        fetcher = GitHubFileFetcher(context.access_token)
        state.data["github_file_fetcher"] = fetcher
        state.data.setdefault("is_file_reachable_fn", fetcher.is_file_reachable)
        state.data.setdefault("list_contents_fn", fetcher.list_repo_contents)
    return fetcher


def github_repo_payload(context: StepContext, state: StepState) -> dict:
    if "repo_payload" not in state.data:
        owner, repo = repo_parts(context)
        try:
            state.data["repo_payload"] = github_client(context, state).get_repo(owner, repo)
        except Exception:
            state.data["repo_payload"] = {}
    return state.data.get("repo_payload") or {}


def github_languages_payload(context: StepContext, state: StepState) -> dict:
    if "languages_payload" not in state.data:
        owner, repo = repo_parts(context)
        try:
            state.data["languages_payload"] = github_client(context, state).get_languages(owner, repo)
        except Exception:
            state.data["languages_payload"] = {}
    return state.data.get("languages_payload") or {}


def github_contributors_payload(context: StepContext, state: StepState) -> list[dict]:
    if "contributors_payload" not in state.data:
        owner, repo = repo_parts(context)
        try:
            state.data["contributors_payload"] = github_client(context, state).get_contributors(owner, repo)
        except Exception:
            state.data["contributors_payload"] = []
    return state.data.get("contributors_payload") or []


def github_license_payload(context: StepContext, state: StepState) -> dict:
    if "license_payload" not in state.data:
        owner, repo = repo_parts(context)
        try:
            state.data["license_payload"] = github_client(context, state).get_license(owner, repo) or {}
        except Exception:
            state.data["license_payload"] = {}
    return state.data.get("license_payload") or {}


def github_release_payload(context: StepContext, state: StepState) -> dict:
    if "release_payload" not in state.data:
        owner, repo = repo_parts(context)
        try:
            state.data["release_payload"] = github_client(context, state).get_latest_release(owner, repo) or {}
        except Exception:
            state.data["release_payload"] = {}
    return state.data.get("release_payload") or {}


def github_commits_payload(context: StepContext, state: StepState) -> list[dict]:
    if "commits_payload" not in state.data:
        owner, repo = repo_parts(context)
        try:
            state.data["commits_payload"] = github_client(context, state).get_commits(owner, repo, per_page=1)
        except Exception:
            state.data["commits_payload"] = []
    return state.data.get("commits_payload") or []


def gitlab_client(context: StepContext, state: StepState) -> GitLabClient:
    client = state.data.get("gitlab_client")
    if client is None:
        client = GitLabClient(context.access_token)
        state.data["gitlab_client"] = client
    return client


def gitlab_file_fetcher(context: StepContext, state: StepState) -> GitLabFileFetcher:
    fetcher = state.data.get("gitlab_file_fetcher")
    if fetcher is None:
        fetcher = GitLabFileFetcher(context.access_token)
        state.data["gitlab_file_fetcher"] = fetcher
        state.data.setdefault("is_file_reachable_fn", fetcher.is_file_reachable)
        state.data.setdefault("list_contents_fn", fetcher.list_repo_contents)
    return fetcher


def gitlab_project_id(context: StepContext) -> str:
    owner, repo = repo_parts(context)
    return quote(f"{owner}/{repo}", safe="")


def gitlab_repo_payload(context: StepContext, state: StepState) -> dict:
    if "repo_payload" not in state.data:
        try:
            state.data["repo_payload"] = gitlab_client(context, state).get_project(gitlab_project_id(context))
        except Exception:
            state.data["repo_payload"] = {}
    return state.data.get("repo_payload") or {}


def gitlab_languages_payload(context: StepContext, state: StepState) -> dict:
    if "languages_payload" not in state.data:
        try:
            state.data["languages_payload"] = gitlab_client(context, state).get_languages(gitlab_project_id(context))
        except Exception:
            state.data["languages_payload"] = {}
    return state.data.get("languages_payload") or {}


def gitlab_contributors_payload(context: StepContext, state: StepState) -> list[dict]:
    if "contributors_payload" not in state.data:
        try:
            state.data["contributors_payload"] = gitlab_client(context, state).get_contributors(gitlab_project_id(context))
        except Exception:
            state.data["contributors_payload"] = []
    return state.data.get("contributors_payload") or []


def gitlab_license_payload(context: StepContext, state: StepState) -> dict:
    if "license_payload" not in state.data:
        try:
            state.data["license_payload"] = gitlab_client(context, state).get_license(gitlab_project_id(context)) or {}
        except Exception:
            state.data["license_payload"] = {}
    return state.data.get("license_payload") or {}


def gitlab_release_payload(context: StepContext, state: StepState) -> dict:
    if "release_payload" not in state.data:
        try:
            state.data["release_payload"] = gitlab_client(context, state).get_latest_release(gitlab_project_id(context)) or {}
        except Exception:
            state.data["release_payload"] = {}
    return state.data.get("release_payload") or {}


def gitlab_commits_payload(context: StepContext, state: StepState) -> list[dict]:
    if "commits_payload" not in state.data:
        try:
            state.data["commits_payload"] = gitlab_client(context, state).get_commits(gitlab_project_id(context), per_page=1)
        except Exception:
            state.data["commits_payload"] = []
    return state.data.get("commits_payload") or []

