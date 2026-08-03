"""GitLab source code URL metadata step."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabSourceCodeStep(ExtractionPlugin):
    name = "gitlab.extract_source_code"
    platforms = {"gitlab"}
    extracts = {"https://codemeta.github.io/terms/hasSourceCode"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        web_url = project.get("web_url")
        if not web_url:
            return state
        hasSourceCode =web_url
        state.metadata_collector.collect(self.name, "https://codemeta.github.io/terms/hasSourceCode", hasSourceCode)
        return state



