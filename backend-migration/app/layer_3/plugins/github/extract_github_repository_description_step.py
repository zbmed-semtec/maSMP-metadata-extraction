"""Extract repository ``description`` from the GitHub API payload."""

from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin

class ExtractGithubRepositoryDescriptionStep(ExtractionPlugin):
    name = "github.extract_repository_description"
    extracts = {"https://schema.org/description"}
    platforms = {"github"}
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)

        description = repo_data.get("description")
        if description is not None:
            state.metadata_collector.collect(self.name, "https://schema.org/description", description)

        return state



