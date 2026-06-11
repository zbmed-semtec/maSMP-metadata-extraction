"""Shared helpers for requirements-link discovery steps."""
from __future__ import annotations

from typing import Any, Callable, Iterable, Optional

from app.layer_3.utils.url_pattern_matcher import URLPatternMatcher

DEFAULT_REQUIREMENT_FILES = frozenset({
    "requirements.txt",
    "requirements-dev.txt",
    "dev-requirements.txt",
    "requirements.in",
    "constraints.txt",
    "environment.yml",
    "environment.yaml",
    "Pipfile",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
})


def discover_requirement_urls_from_state(
    *,
    state_data: dict[str, Any],
    platform: str,
    repo_url: str,
) -> list[str]:
    """Extract requirements links using callbacks injected into step state."""
    list_contents_fn = state_data.get("list_contents_fn")
    is_file_reachable_fn = state_data.get("is_file_reachable_fn")
    if not callable(is_file_reachable_fn):
        return []

    owner, repo = URLPatternMatcher.extract_repo_info(repo_url)
    if not owner or not repo:
        return []
    if repo.endswith(".git"):
        repo = repo[:-4]

    base_url = (state_data.get("normalized_repo_url") or repo_url or "").rstrip("/")
    branches = _branches_from_state(state_data)

    def _list_contents(owner_arg: str, repo_arg: str, path: str) -> Iterable[dict]:
        if callable(list_contents_fn):
            listed = list_contents_fn(owner_arg, repo_arg, path)
            if listed is None:
                return []
            return listed
        return []

    if platform == "gitlab":
        return _discover_software_requirement_urls(
            owner,
            repo,
            list_contents_fn=_list_contents if callable(list_contents_fn) else None,
            is_file_reachable_fn=is_file_reachable_fn,
            build_blob_url_fn=lambda branch, path: (
                f"{base_url}/-/blob/{branch}/{path}"
            ),
            branches=branches,
        )

    return _discover_software_requirement_urls(
        owner,
        repo,
        list_contents_fn=_list_contents if callable(list_contents_fn) else None,
        is_file_reachable_fn=is_file_reachable_fn,
        build_blob_url_fn=lambda branch, path: f"{base_url}/blob/{branch}/{path}",
        branches=branches,
    )


def _branches_from_state(state_data: dict[str, Any]) -> tuple[str, ...]:
    repo_payload = state_data.get("repo_payload") or {}
    default_branch = repo_payload.get("default_branch")
    ordered: list[str] = []
    for branch in (default_branch, "main", "master"):
        if branch and branch not in ordered:
            ordered.append(branch)
    return tuple(ordered) if ordered else ("main", "master")


def _discover_software_requirement_urls(
    owner: str,
    repo: str,
    *,
    list_contents_fn: Callable[[str, str, str], Iterable[dict]] | None,
    is_file_reachable_fn: Callable[[str], bool],
    build_blob_url_fn: Callable[[str, str], str],
    branches: tuple[str, ...] = ("main", "master"),
    requirement_files: set[str] | None = None,
    max_depth: int = 3,
) -> list[str]:
    files = requirement_files or set(DEFAULT_REQUIREMENT_FILES)
    requirement_urls: list[str] = []
    seen_paths: set[str] = set()

    def _try_add_url(url: str, path_key: str) -> bool:
        if path_key in seen_paths:
            return False
        if is_file_reachable_fn(url):
            requirement_urls.append(url)
            seen_paths.add(path_key)
            return True
        return False

    def _add_from_item(item: dict) -> None:
        item_type = item.get("type")
        name = item.get("name")
        item_path = item.get("path") or name
        if not name or not item_path:
            return
        if item_type not in ("file", "blob"):
            return
        if name not in files and not name.endswith(".lock"):
            return

        html_url = item.get("html_url") or item.get("web_url")
        if html_url and _try_add_url(html_url, item_path):
            return

        for branch in branches:
            file_url = build_blob_url_fn(branch, item_path)
            if _try_add_url(file_url, item_path):
                return

    def _walk(path: str, depth: int) -> None:
        if depth > max_depth or not callable(list_contents_fn):
            return
        try:
            contents = list(list_contents_fn(owner, repo, path))
        except Exception:
            return
        if not contents:
            return
        for item in contents:
            item_type = item.get("type")
            name = item.get("name")
            item_path = item.get("path") or name
            if not name or not item_path:
                continue
            if item_type in ("file", "blob"):
                _add_from_item(item)
            elif item_type in ("dir", "tree") and depth < max_depth:
                _walk(item_path, depth + 1)

    if callable(list_contents_fn):
        _walk("", 0)

    if not requirement_urls:
        for branch in branches:
            for filename in files:
                if filename in seen_paths:
                    continue
                file_url = build_blob_url_fn(branch, filename)
                _try_add_url(file_url, filename)

    return requirement_urls


def discover_software_requirement_urls(
    owner: str,
    repo: str,
    *,
    list_contents_fn: Optional[Callable[[str, str, str], Iterable[dict]]],
    is_file_reachable_fn: Callable[[str], bool],
    build_blob_url_fn: Callable[[str, str], str],
    branches: tuple[str, ...] = ("main", "master"),
    requirement_files: Optional[set[str]] = None,
    max_depth: int = 3,
) -> list[str]:
    return _discover_software_requirement_urls(
        owner,
        repo,
        list_contents_fn=list_contents_fn,
        is_file_reachable_fn=is_file_reachable_fn,
        build_blob_url_fn=build_blob_url_fn,
        branches=branches,
        requirement_files=requirement_files,
        max_depth=max_depth,
    )


__all__ = [
    "DEFAULT_REQUIREMENT_FILES",
    "discover_requirement_urls_from_state",
    "discover_software_requirement_urls",
]
