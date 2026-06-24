"""Extract canonical web ``url`` from the GitHub API payload."""
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin

from app.layer_2.extraction_plugin import ExtractionPlugin

class ExtractGithubRepositoryWebUrlStep(ExtractionPlugin):
    name = "github.extract_repository_web_url"
    extracts = {"url"}
    platforms = {"github"}
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        
        url = repo_data.get("html_url")
        if url is not None:
            state.metadata_collector.collect(self.name, 'url', url)

        return state



