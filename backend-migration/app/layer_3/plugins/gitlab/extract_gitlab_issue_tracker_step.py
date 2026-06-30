"""GitLab issue tracker metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState

from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabIssueTrackerStep(ExtractionPlugin):
    name = "gitlab.extract_issue_tracker"
    platforms = {"gitlab"}
    extracts = {"issueTracker", "discussionUrl"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        project = self.plugin_manager.get('platform-payloads-plugin').gitlab_repo_payload(context, state)
        web_url = project.get("web_url")
        if not web_url:
            return state
        issueTracker = web_url + "/-/issues"
        state.metadata_collector.collect(self.name, "issueTracker", issueTracker)
        if project.get("operations_access_level") == "enabled":
            discussionUrl = web_url + "/-/discussions"
            state.metadata_collector.collect(self.name, "discussionUrl", discussionUrl)
        return state


def gitlab_issue_tracker_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabIssueTrackerStep(),)
