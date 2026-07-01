"""GitLab access metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabAccessStep(ExtractionPlugin):
    name = "gitlab.extract_access"
    platforms = {"gitlab"}
    extracts = {"https://schema.org/conditionOfAccess", "https://schema.org/isAccessibleForFree"}
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        
        visibility = str(project.get("visibility", "")).lower()
        conditionOfAccess = visibility.capitalize() if visibility else None
        isAccessibleForFree = str(visibility == "public") if visibility else None
        if visibility:
            state.metadata_collector.collect(self.name, "https://schema.org/conditionOfAccess", conditionOfAccess)
            state.metadata_collector.collect(self.name, "https://schema.org/isAccessibleForFree", isAccessibleForFree)
        return state

def gitlab_access_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabAccessStep(),)
