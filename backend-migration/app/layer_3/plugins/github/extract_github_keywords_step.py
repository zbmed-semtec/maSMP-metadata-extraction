"""GitHub keyword metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubKeywordsStep(ExtractionPlugin):
    name = "github.extract_keywords"

    extracts = {"https://schema.org/keywords"}
    priority_level = 102
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        topics = repo_data.get("topics") or []
        if topics:
            state.metadata_collector.collect(self.name, "https://schema.org/keywords", topics)
        return state


def github_keyword_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubKeywordsStep(),)
