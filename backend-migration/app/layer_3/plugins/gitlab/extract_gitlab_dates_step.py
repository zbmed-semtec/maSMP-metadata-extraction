"""GitLab date extraction steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabDatesStep(ExtractionPlugin):
    name = "gitlab.extract_dates"
    platforms = {"gitlab"}

    extracts = {"dateCreated","https://schema.org/dateModified","https://schema.org/datePublished"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        
        if project.get("created_at"):
            dateCreated = str(project.get("created_at"))[:10]
            state.metadata_collector.collect(self.name, "dateCreated", dateCreated)
        if project.get("last_activity_at"):
            dateModified = str(project.get("last_activity_at"))[:10]
            state.metadata_collector.collect(self.name, "https://schema.org/dateModified", dateModified)
        date_published = state.data.get("date_published")
        if not date_published:
            commits = ppp.gitlab_commits_payload(context, state)
            date_published = commits[0].get("created_at") if commits else None
        if date_published:
            datePublished = str(date_published)[:10]
            state.metadata_collector.collect(self.name, "https://schema.org/datePublished", datePublished)
        return state

def gitlab_date_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabDatesStep(),)
