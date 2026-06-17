"""GitLab issue tracker metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabIssueTrackerStep(ExtractionPlugin):
    name = "gitlab.extract_issue_tracker"
    platforms = {"gitlab"}
    extracts = {"issueTracker", "codemeta:issueTracker", "discussionUrl"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        web_url = project.get("web_url")
        if not web_url:
            return state
        metadata.issueTracker = web_url + "/-/issues"
        metadata.codemeta_issueTracker = metadata.issueTracker
        if callable(record):
            record("issueTracker")
            record("codemeta_issueTracker")
        if project.get("operations_access_level") == "enabled":
            metadata.discussionUrl = web_url + "/-/discussions"
            if callable(record):
                record("discussionUrl")
        return state


def gitlab_issue_tracker_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabIssueTrackerStep(),)
