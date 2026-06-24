"""GitHub download URL metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubDownloadUrlStep(ExtractionPlugin):
    name = "github.extract_download_url"

    extracts = {"downloadUrl"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        archive_url = repo_data.get("archive_url", "")
        if archive_url:
            downloadUrl = archive_url.replace("{archive_format}{/ref}", "zipball/master")
            state.metadata_collector.collect(self.name, "downloadUrl", downloadUrl)
        return state


def github_download_url_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubDownloadUrlStep(),)
