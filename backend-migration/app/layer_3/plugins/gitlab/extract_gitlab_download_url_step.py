"""GitLab download URL metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin

from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabDownloadUrlStep(ExtractionPlugin):
    name = "gitlab.extract_download_url"
    platforms = {"gitlab"}
    extracts = {
        "downloadUrl"
    }

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        
        web_url = project.get("web_url")
        name = project.get("name")
        if web_url and name:
            downloadUrl = f"{web_url}/-/archive/master/{name}-master.zip"
            state.metadata_collector.collect(self.name, "downloadUrl", downloadUrl)
        return state


def gitlab_download_url_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabDownloadUrlStep(),)
