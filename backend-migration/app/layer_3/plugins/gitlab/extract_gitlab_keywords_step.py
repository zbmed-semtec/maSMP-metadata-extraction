"""GitLab keyword metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabKeywordsStep(ExtractionPlugin):
    name = "gitlab.extract_keywords"
    platforms = {"gitlab"}
    extracts = {"keywords"}
    priority_level = 101

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        tag_list = project.get("tag_list") or []
        if tag_list:
            state.data["extracted_platform_keywords"] = list(tag_list)
        return state


def gitlab_keyword_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabKeywordsStep(),)
