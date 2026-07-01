"""GitHub VCS metadata steps."""

from app.layer_1.entities.shared_primitives import VersionControlSystem
from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubVcsStep(ExtractionPlugin):
    name = "github.extract_vcs"
    extracts = {"https://discovery.biothings.io/ns/maSMP/versionControlSystem"}
    platforms = {"github"}
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        masmp_versionControlSystem = VersionControlSystem.create_git(vcs_type="SoftwareSourceCode")
        state.metadata_collector.collect(self.name, "https://discovery.biothings.io/ns/maSMP/versionControlSystem", masmp_versionControlSystem)
        return state


def github_vcs_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubVcsStep(),)
