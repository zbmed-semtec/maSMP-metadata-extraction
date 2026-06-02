"""GitLab contributor metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_contributors_payload,
)


class ExtractGitlabContributorsStep(ExtractionStep):
    name = "gitlab.extract_contributors"

    def run(self, context: StepContext, state: StepState) -> StepState:
        payload = gitlab_contributors_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        if payload:
            metadata.contributor = [
                {"@type": "Person", "name": c.get("name"), "email": c.get("email")}
                for c in payload
            ]
            if callable(record):
                record("contributor")
        return state


def gitlab_contributor_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabContributorsStep(),)
