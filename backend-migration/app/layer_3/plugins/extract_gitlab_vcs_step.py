"""GitLab VCS metadata steps."""

from app.layer_1.entities.shared_primitives import VersionControlSystem
from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabVcsStep(ExtractionPlugin):
    name = "gitlab.extract_vcs"
    platforms = {"gitlab"}
    extracts = $maSMP:versionControlSystem"}
    priority_level = 99

    def extract(self, context: StepContext, state: StepState) -> StepState:
        metadata = state.metadata
        record = state.data.get("record_field")
        metadata.masmp_versionControlSystem = VersionControlSystem.create_git(vcs_type="SoftwareSourceCode")
        if callable(record):
            record("masmp_versionControlSystem")
        return state


def gitlab_vcs_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabVcsStep(),)
