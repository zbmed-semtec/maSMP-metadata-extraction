"""GitHub access metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState

from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubAccessStep(ExtractionPlugin):
    name = "github.extract_access"
    extracts = {'conditionsOfAccess', 'isAccessibleForFree'}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.github_repo_payload(context, state)
        is_private = bool(repo_data.get("private", False))
        conditionsOfAccess = "Private" if is_private else "Public"
        isAccessibleForFree = str(not is_private)
        state.metadata_collector.collect(
            self.name, "conditionsOfAccess", conditionsOfAccess)
        state.metadata_collector.collect(
            self.name, "isAccessibleForFree", isAccessibleForFree)
        return state


def github_access_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubAccessStep(),)
