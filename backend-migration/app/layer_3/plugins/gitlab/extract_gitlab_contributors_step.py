"""GitLab contributor metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabContributorsStep(ExtractionPlugin):
    name = "gitlab.extract_contributors"
    platforms = {"gitlab"}
    extracts = {"https://schema.org/contributor"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        payload = ppp.gitlab_contributors_payload(context, state)
        
        if payload:
            contributor = [
                {"@type": "Person", "https://schema.org/name": c.get("name"), "email": c.get("email")}
                for c in payload
            ]
            state.metadata_collector.collect(self.name, "https://schema.org/contributor", contributor)
        return state


def gitlab_contributor_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabContributorsStep(),)
