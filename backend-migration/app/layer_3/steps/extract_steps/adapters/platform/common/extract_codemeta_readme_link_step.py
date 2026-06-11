"""Resolve ``codemeta_readme`` from prepared README URL candidates."""
from __future__ import annotations

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.common.helpers.metadata_link_candidates import (
    first_reachable_url,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import record_field


class ExtractCodemetaReadmeLinkStep:
    """Set ``metadata.codemeta_readme`` from the first reachable candidate URL."""

    name = "platform.extract_codemeta_readme_link"

    def run(self, context: StepContext, state: StepState) -> StepState:
        candidates = state.data.get("metadata_file_candidates") or {}
        is_file_reachable_fn = state.data.get("is_file_reachable_fn")
        if not callable(is_file_reachable_fn):
            return state

        readme_url = first_reachable_url(candidates.get("readme") or [], is_file_reachable_fn)
        if readme_url:
            state.metadata.codemeta_readme = readme_url
            record_field(state, "codemeta_readme")

        return state


__all__ = ["ExtractCodemetaReadmeLinkStep"]
