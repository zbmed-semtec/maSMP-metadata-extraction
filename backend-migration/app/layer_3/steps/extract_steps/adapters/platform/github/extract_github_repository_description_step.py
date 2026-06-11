"""Extract repository ``description`` from the GitHub API payload."""
from __future__ import annotations

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
    record_field,
)


class ExtractGithubRepositoryDescriptionStep:
    name = "github.extract_repository_description"

    def run(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        metadata.description = repo_data.get("description")
        if metadata.description is not None and record:
            record("description")

        return state


__all__ = ["ExtractGithubRepositoryDescriptionStep"]
