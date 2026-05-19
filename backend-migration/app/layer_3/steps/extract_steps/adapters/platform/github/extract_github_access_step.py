"""GitHub access metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
)


class ExtractGithubAccessStep:
    name = "github.extract_access"

    def run(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        is_private = bool(repo_data.get("private", False))
        metadata.conditionsOfAccess = "Private" if is_private else "Public"
        metadata.isAccessibleForFree = str(not is_private)
        if callable(record):
            record("conditionsOfAccess")
            record("isAccessibleForFree")
        return state


def github_access_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubAccessStep(),)
