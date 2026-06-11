"""Repository file content helpers used by file extraction steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_file_fetcher,
    gitlab_file_fetcher,
    repo_parts,
)


def repository_file_content(
    context: StepContext,
    state: StepState,
    data_key: str,
    file_names: tuple[str, ...],
) -> str:
    """Return cached content for the first matching repository file."""
    cached = state.data.get(data_key)
    if cached:
        return cached

    owner, repo = repo_parts(context)
    if not owner or not repo:
        return ""

    fetcher = (
        github_file_fetcher(context, state)
        if context.platform == "github"
        else gitlab_file_fetcher(context, state)
    )
    for branch in ("main", "master"):
        for file_name in file_names:
            content = fetcher.fetch_file_from_repo(owner, repo, file_name, branch)
            if content:
                state.data[data_key] = content
                return content
    state.data[data_key] = ""
    return ""

