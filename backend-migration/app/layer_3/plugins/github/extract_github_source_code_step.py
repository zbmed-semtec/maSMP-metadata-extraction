"""GitHub source code URL metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubSourceCodeStep(ExtractionPlugin):
    name = "github.extract_source_code"
    extracts = {"hasSourceCode", "codemeta:hasSourceCode"}
    platforms = {"github"}
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        html_url = repo_data.get("html_url")
        if not html_url:
            return state
        source_url = f"{html_url}#id"
        hasSourceCode =source_url
        codemeta_hasSourceCode =source_url
        state.metadata_collector.collect(self.name, "hasSourceCode", hasSourceCode)
        state.metadata_collector.collect(self.name, "codemeta_hasSourceCode", codemeta_hasSourceCode)
        return state


def github_source_code_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubSourceCodeStep(),)




