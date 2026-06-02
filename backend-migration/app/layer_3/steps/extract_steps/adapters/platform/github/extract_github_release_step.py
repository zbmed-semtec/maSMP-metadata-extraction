"""GitHub release/version metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_commits_payload,
    github_release_payload,
    record_field,
)


class ExtractGithubReleaseStep(ExtractionStep):
    name = "github.extract_release"

    def run(self, context: StepContext, state: StepState) -> StepState:
        release = github_release_payload(context, state)
        if not release:
            state.metadata.has_release = False
            return state

        state.metadata.softwareVersion = release.get("tag_name")
        state.metadata.has_release = True
        record_field(state, "softwareVersion")

        release_date = str(release.get("published_at") or "")[:10]
        commits = github_commits_payload(context, state)
        commit_date = ""
        if commits:
            commit_date = str(
                commits[0].get("commit", {}).get("committer", {}).get("date", "")
            )[:10]
        if not release_date or not commit_date or commit_date <= release_date:
            state.metadata.version = release.get("tag_name")
            record_field(state, "version")
        return state


def github_release_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubReleaseStep(),)


__all__ = ["ExtractGithubReleaseStep", "github_release_steps"]

