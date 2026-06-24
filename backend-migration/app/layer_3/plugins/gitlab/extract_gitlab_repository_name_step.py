"""Extract project ``name`` from the GitLab API payload."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabRepositoryNameStep(ExtractionPlugin):
    name = "gitlab.extract_repository_name"
    platforms = {"gitlab"}
    extracts = {"name"}
    
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        name = project.get("name")
        if name is not None:
            state.metadata_collector.collect(self.name, 'name', name)

        return state



