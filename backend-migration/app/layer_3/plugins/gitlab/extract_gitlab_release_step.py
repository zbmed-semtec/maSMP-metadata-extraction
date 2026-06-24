"""GitLab release/version metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin

from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabReleaseStep(ExtractionPlugin):
    name = "gitlab.extract_release"
    platforms = {"gitlab"}
    extracts = {"version", "softwareVersion"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        release = ppp.gitlab_release_payload(context, state)
        if not release:
            has_release =False
            return state
        softwareVersion =release.get("tag_name")
        version =release.get("tag_name")
        has_release =True
        state.metadata_collector.collect(self.name, "softwareVersion", softwareVersion)
        state.metadata_collector.collect(self.name, "version", version)
        return state


def gitlab_release_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabReleaseStep(),)




