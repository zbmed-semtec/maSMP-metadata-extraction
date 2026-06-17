"""GitLab access metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
)
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabAccessStep(ExtractionPlugin):
    name = "gitlab.extract_access"
    platforms = {"gitlab"}
    extracts = {"conditionsOfAccess", "isAccessibleForFree"}
    def extract(self, context: StepContext, state: StepState) -> StepState:
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
