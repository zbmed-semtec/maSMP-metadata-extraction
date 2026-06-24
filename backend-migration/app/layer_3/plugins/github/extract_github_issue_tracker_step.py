"""GitHub issue tracker metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubIssueTrackerStep(ExtractionPlugin):
    name = "github.extract_issue_tracker"

    extracts = {"issueTracker", "codemeta:issueTracker", "discussionUrl"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        html_url = repo_data.get("html_url")
        if not html_url:
            return state
        issueTracker = f"{html_url}/issues"
        codemeta_issueTracker = issueTracker
        state.metadata_collector.collect(self.name, "issueTracker", issueTracker)
        state.metadata_collector.collect(self.name, "codemeta_issueTracker", codemeta_issueTracker)
        if repo_data.get("has_discussions"):
            discussionUrl = f"{html_url}/discussions"
            state.metadata_collector.collect(self.name, "discussionUrl", discussionUrl)
        return state


def github_issue_tracker_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubIssueTrackerStep(),)
