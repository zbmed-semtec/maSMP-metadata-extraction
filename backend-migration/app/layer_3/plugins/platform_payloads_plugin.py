"""Lazy platform payload helpers for source-specific extraction steps."""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse, quote
from app.layer_2.base_plugin import BasePlugin

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.github.github_client_plugin import GitHubClient
from app.layer_3.plugins.gitlab.gitlab_client_plugin import GitLabClient
from app.layer_3.plugins.github_file_fetcher import GitHubFileFetcher
from app.layer_3.plugins.gitlab_file_fetcher import GitLabFileFetcher
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher

class PlatformPayloadsPlugin(BasePlugin):

    name = "platform-payloads-plugin"

    def repo_parts(self, context: ExtractionContext) -> tuple[str, str]:
        upm : URLPatternMatcher = self.plugin_manager.get("url-pattern-matcher-plugin")
        owner, repo = upm.extract_repo_info(context.repo_url)
        return owner or "", repo or ""

    def github_client(self, context: ExtractionContext, state: ExtractionState) -> GitHubClient:
        client = state.data.get("github_client")
        if client is None:
            client = GitHubClient(context.access_token)
            state.data['github_client'] = client
        return client

    def github_file_fetcher(self, context: ExtractionContext, state: ExtractionState) -> GitHubFileFetcher:
        fetcher = state.data.get("github_file_fetcher")
        if fetcher is None:
            fetcher = GitHubFileFetcher(context.access_token)
            state.data["github_file_fetcher"] = fetcher
            state.data.setdefault("is_file_reachable_fn", fetcher.is_file_reachable)
            state.data.setdefault("list_contents_fn", fetcher.list_repo_contents)
        return fetcher


    def github_repo_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "repo_payload" not in state.data:
            owner, repo = self.repo_parts(context)
            try:
                state.data["repo_payload"] = self.github_client(context, state).get_repo(owner, repo)
            except Exception:
                state.data["repo_payload"] = {}
        return state.data.get("repo_payload") or {}


    def github_languages_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "languages_payload" not in state.data:
            owner, repo = self.repo_parts(context)
            try:
                state.data["languages_payload"] = self.github_client(context, state).get_languages(owner, repo)
            except Exception:
                state.data["languages_payload"] = {}
        return state.data.get("languages_payload") or {}


    def github_contributors_payload(self, context: ExtractionContext, state: ExtractionState) -> list[dict]:
        if "contributors_payload" not in state.data:
            owner, repo = self.repo_parts(context)
            try:
                state.data["contributors_payload"] = self.github_client(context, state).get_contributors(owner, repo)
            except Exception:
                state.data["contributors_payload"] = []
        return state.data.get("contributors_payload") or []


    def github_license_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "license_payload" not in state.data:
            owner, repo = self.repo_parts(context)
            try:
                state.data["license_payload"] = self.github_client(context, state).get_license(owner, repo) or {}
            except Exception:
                state.data["license_payload"] = {}
        return state.data.get("license_payload") or {}


    def github_release_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "release_payload" not in state.data:
            owner, repo = self.repo_parts(context)
            try:
                state.data["release_payload"] = self.github_client(context, state).get_latest_release(owner, repo) or {}
            except Exception:
                state.data["release_payload"] = {}
        return state.data.get("release_payload") or {}


    def github_commits_payload(self, context: ExtractionContext, state: ExtractionState) -> list[dict]:
        if "commits_payload" not in state.data:
            owner, repo = self.repo_parts(context)
            try:
                state.data["commits_payload"] = self.github_client(context, state).get_commits(owner, repo, per_page=1)
            except Exception:
                state.data["commits_payload"] = []
        return state.data.get("commits_payload") or []

    def gitlab_client(self, context: ExtractionContext, state: ExtractionState) -> GitLabClient:
        client = state.data.get("gitlab_client")
        if client is None:
            client = GitHubClient(context.access_token)
            state.data['gitlab_client'] = client
        return client

    def gitlab_file_fetcher(self, context: ExtractionContext, state: ExtractionState) -> GitLabFileFetcher:
        fetcher = state.data.get("gitlab_file_fetcher")
        if fetcher is None:
            fetcher = GitLabFileFetcher(context.access_token)
            state.data["gitlab_file_fetcher"] = fetcher
            state.data.setdefault("is_file_reachable_fn", fetcher.is_file_reachable)
            state.data.setdefault("list_contents_fn", fetcher.list_repo_contents)
        return fetcher


    def gitlab_project_id(self, context: ExtractionContext) -> str:
        owner, repo = self.repo_parts(context)
        return quote(f"{owner}/{repo}", safe="")


    def gitlab_repo_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "repo_payload" not in state.data:
            try:
                state.data["repo_payload"] = self.gitlab_client(context, state).get_project(self.gitlab_project_id(context))
            except Exception:
                state.data["repo_payload"] = {}
        return state.data.get("repo_payload") or {}


    def gitlab_languages_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "languages_payload" not in state.data:
            try:
                state.data["languages_payload"] = self.gitlab_client(context, state).get_languages(self.gitlab_project_id(context))
            except Exception:
                state.data["languages_payload"] = {}
        return state.data.get("languages_payload") or {}


    def gitlab_contributors_payload(self, context: ExtractionContext, state: ExtractionState) -> list[dict]:
        if "contributors_payload" not in state.data:
            try:
                state.data["contributors_payload"] = self.gitlab_client(context, state).get_contributors(self.gitlab_project_id(context))
            except Exception:
                state.data["contributors_payload"] = []
        return state.data.get("contributors_payload") or []


    def gitlab_license_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "license_payload" not in state.data:
            try:
                state.data["license_payload"] = self.gitlab_client(context, state).get_license(self.gitlab_project_id(context)) or {}
            except Exception:
                state.data["license_payload"] = {}
        return state.data.get("license_payload") or {}


    def gitlab_release_payload(self, context: ExtractionContext, state: ExtractionState) -> dict:
        if "release_payload" not in state.data:
            try:
                state.data["release_payload"] = self.gitlab_client(context, state).get_latest_release(self.gitlab_project_id(context)) or {}
            except Exception:
                state.data["release_payload"] = {}
        return state.data.get("release_payload") or {}


    def gitlab_commits_payload(self, context: ExtractionContext, state: ExtractionState) -> list[dict]:
        if "commits_payload" not in state.data:
            try:
                state.data["commits_payload"] = self.gitlab_client(context, state).get_commits(self.gitlab_project_id(context), per_page=1)
            except Exception:
                state.data["commits_payload"] = []
        return state.data.get("commits_payload") or []

