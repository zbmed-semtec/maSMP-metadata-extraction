"""GitLab VCS metadata steps."""

from app.layer_1.entities.shared_primitives import VersionControlSystem
from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabVcsStep(ExtractionPlugin):
    name = "gitlab.extract_vcs"
    platforms = {"gitlab"}
    extracts = {"versionControlSystem"}
    priority_level = 99

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        
        masmp_versionControlSystem = VersionControlSystem.create_git(vcs_type="SoftwareSourceCode")
        state.metadata_collector.collect(self.name, "masmp:versionControlSystem", masmp_versionControlSystem)
        return state


def gitlab_vcs_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabVcsStep(),)
