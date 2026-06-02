"""GitLab access metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
)


class ExtractGitlabAccessStep(ExtractionStep):
    name = "gitlab.extract_access"

    def run(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        visibility = str(project.get("visibility", "")).lower()
        metadata.conditionsOfAccess = visibility.capitalize() if visibility else None
        metadata.isAccessibleForFree = str(visibility == "public") if visibility else None
        if callable(record) and visibility:
            record("conditionsOfAccess")
            record("isAccessibleForFree")
        return state


def gitlab_access_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabAccessStep(),)
