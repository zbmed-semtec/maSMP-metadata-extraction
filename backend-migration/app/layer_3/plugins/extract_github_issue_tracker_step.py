"""GitHub issue tracker metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubIssueTrackerStep(ExtractionPlugin):
    name = "github.extract_issue_tracker"

    extracts = {"issueTracker", "codemeta:issueTracker", "discussionUrl"}
    platforms = {"github"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        html_url = repo_data.get("html_url")
        if not html_url:
            return state
        metadata.issueTracker = f"{html_url}/issues"
        metadata.codemeta_issueTracker = metadata.issueTracker
        if callable(record):
            record("issueTracker")
            record("codemeta_issueTracker")
        if repo_data.get("has_discussions"):
            metadata.discussionUrl = f"{html_url}/discussions"
            if callable(record):
                record("discussionUrl")
        return state


def github_issue_tracker_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubIssueTrackerStep(),)
