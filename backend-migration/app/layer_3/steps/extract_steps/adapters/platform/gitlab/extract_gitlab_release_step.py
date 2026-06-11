"""GitLab release/version metadata step."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_release_payload,
    record_field,
)


class ExtractGitlabReleaseStep:
    name = "gitlab.extract_release"

    def run(self, context: StepContext, state: StepState) -> StepState:
        release = gitlab_release_payload(context, state)
        if not release:
            state.metadata.has_release = False
            return state
        state.metadata.softwareVersion = release.get("tag_name")
        state.metadata.version = release.get("tag_name")
        state.metadata.has_release = True
        record_field(state, "softwareVersion")
        record_field(state, "version")
        return state


def gitlab_release_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabReleaseStep(),)


__all__ = ["ExtractGitlabReleaseStep", "gitlab_release_steps"]

