"""GitLab issue tracker metadata steps."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabIssueTrackerStep(ExtractionPlugin):
    name = "gitlab.extract_issue_tracker"
    platforms = {"gitlab"}
    extracts = {"https://schema.org/issueTracker", "https://schema.org/discussionUrl"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        project = self.plugin_manager.get('platform-payloads-plugin').gitlab_repo_payload(context, state)
        web_url = project.get("web_url")
        if not web_url:
            return state
        issueTracker = web_url + "/-/issues"
        state.metadata_collector.collect(self.name, "https://schema.org/issueTracker", issueTracker)
        if project.get("operations_access_level") == "enabled":
            discussionUrl = web_url + "/-/discussions"
            state.metadata_collector.collect(self.name, "https://schema.org/discussionUrl", discussionUrl)
        return state
