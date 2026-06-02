"""Extract Software Heritage archivedAt candidates."""

from collections.abc import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.software_heritage.helpers.extract_archive import (
    lookup_software_heritage,
)


class ExtractSoftwareHeritageArchivedUrlStep:
    """Extract Software Heritage candidates for metadata.archivedAt."""

    name = "software_heritage.extract_archived_url"

    def __init__(
        self,
        lookup_fn: Callable[[str], str | None] | None = None,
    ) -> None:
        self._lookup_fn = lookup_fn or lookup_software_heritage

    def run(self, context: StepContext, state: StepState) -> StepState:
        if "extracted_software_heritage_archive_url" in state.data:
            return state
        state.data["extracted_software_heritage_archive_url"] = self._lookup_fn(context.repo_url)
        return state


__all__ = ["ExtractSoftwareHeritageArchivedUrlStep"]
