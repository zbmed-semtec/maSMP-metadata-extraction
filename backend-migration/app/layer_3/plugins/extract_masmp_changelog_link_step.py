"""Resolve ``masmp_changelog`` from prepared CHANGELOG URL candidates."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.common.helpers.metadata_link_candidates import (
    first_reachable_url,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import record_field


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractMasmpChangelogLinkStep(ExtractionPlugin):
    """Set ``metadata.masmp_changelog`` from the first reachable candidate URL."""

    name = "platform.extract_masmp_changelog_link"
    extracts = {"maSMP:changelog"}
    platforms = {"github", "gitlab"}


    def extract(self, context: StepContext, state: StepState) -> StepState:
        candidates = state.data.get("metadata_file_candidates") or {}
        is_file_reachable_fn = state.data.get("is_file_reachable_fn")
        if not callable(is_file_reachable_fn):
            return state

        changelog_url = first_reachable_url(candidates.get("changelog") or [], is_file_reachable_fn)
        if changelog_url:
            state.metadata.masmp_changelog = changelog_url
            record_field(state, "masmp_changelog")

        return state


__all__ = ["ExtractMasmpChangelogLinkStep"]
