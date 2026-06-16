"""GitLab date extraction steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_commits_payload,
    gitlab_repo_payload,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabDatesStep(ExtractionPlugin):
    name = "gitlab.extract_dates"
    platforms = {"gitlab"}

    extracts = {
        "dateCreated"
        ,"dateModified"
        ,"datePublished"
    }

    def extract(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        if project.get("created_at"):
            metadata.dateCreated = str(project.get("created_at"))[:10]
            if callable(record):
                record("dateCreated")
        if project.get("last_activity_at"):
            metadata.dateModified = str(project.get("last_activity_at"))[:10]
            if callable(record):
                record("dateModified")
        date_published = state.data.get("date_published")
        if not date_published:
            commits = gitlab_commits_payload(context, state)
            date_published = commits[0].get("created_at") if commits else None
        if date_published:
            metadata.datePublished = str(date_published)[:10]
            if callable(record):
                record("datePublished")
        return state


def gitlab_date_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabDatesStep(),)
