"""GitHub date extraction steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState


from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


class ExtractGithubDatesStep(ExtractionPlugin):
    name = "github.extract_dates"

    extracts = {"dateCreated", "dateModified", "datePublished"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        if repo_data.get("created_at"):
            state.metadata_collector.collect(self.name, "dateCreated", repo_data.get("created_at"))
        if repo_data.get("updated_at"):
            state.metadata_collector.collect(self.name, "dateModified", repo_data.get("updated_at"))
        if repo_data.get("pushed_at"):
            state.metadata_collector.collect(self.name, "datePublished", repo_data.get("pushed_at"))
        return state


def github_date_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubDatesStep(),)
