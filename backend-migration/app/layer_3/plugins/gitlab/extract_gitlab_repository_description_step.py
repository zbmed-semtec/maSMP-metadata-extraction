"""Extract project ``description`` from the GitLab API payload."""

from typing import Callable

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabRepositoryDescriptionStep(ExtractionPlugin):
    name = "gitlab.extract_repository_description"
    platforms = {"gitlab"}
    extracts = {"description"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        
        description = project.get("description")
        if description:
            state.metadata_collector.collect(self.name, 'description', description)

        return state



