"""GitHub release/version metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin

from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubReleaseStep(ExtractionPlugin):
    name = "github.extract_release"

    extracts = {"https://schema.org/version","https://schema.org/softwareVersion"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        release = ppp.github_release_payload(context, state)
        if not release:
            has_release = False
            return state

        softwareVersion = release.get("tag_name")
        state.metadata_collector.collect(self.name, 'hasRelease', True)
        state.metadata_collector.collect(self.name, "https://schema.org/softwareVersion", softwareVersion)
        state.metadata_collector.collect(self.name, "https://schema.org/version", softwareVersion)

        release_date = str(release.get("published_at") or "")[:10]
        commits = ppp.github_commits_payload(context, state)
        commit_date = ""
        if commits:
            commit_date = str(
                commits[0].get("commit", {}).get("committer", {}).get("date", "")
            )[:10]
        if not release_date or not commit_date or commit_date <= release_date:
            version =release.get("tag_name")
            state.metadata_collector.collect(self.name, "https://schema.org/version", version)
        return state


def github_release_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubReleaseStep(),)




