"""Extract canonical web ``url`` from the GitLab API payload."""

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
    record_field,
)


class ExtractGitlabRepositoryWebUrlStep:
    name = "gitlab.extract_repository_web_url"

    def run(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        metadata.url = project.get("web_url")
        if metadata.url is not None and record:
            record("url")

        return state


__all__ = ["ExtractGitlabRepositoryWebUrlStep"]
