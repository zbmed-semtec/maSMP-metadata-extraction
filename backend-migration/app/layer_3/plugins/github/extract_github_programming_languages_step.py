"""GitHub programming language metadata step."""

from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin

class ExtractGithubProgrammingLanguagesStep(ExtractionPlugin):
    name = "github.extract_programming_languages"

    extracts = {"programmingLanguage"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        languages = ppp.github_languages_payload(context, state)
        if languages:
            programmingLanguage =list(languages.keys())
            state.metadata_collector.collect(self.name, "programmingLanguage", programmingLanguage)
        return state

def github_programming_language_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubProgrammingLanguagesStep(),)




