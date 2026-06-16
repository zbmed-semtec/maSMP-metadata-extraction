"""Extract Software Heritage archivedAt candidates."""

from collections.abc import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.software_heritage.helpers.extract_archive import (
    lookup_software_heritage,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractSoftwareHeritageArchivedUrlStep(ExtractionPlugin):
    """Extract Software Heritage candidates for metadata.archivedAt."""

    name = "software_heritage.extract_archived_url"
    platforms = {"gitlab", "github"}
    extracts = {"archivedAt"}


    def extract(self, context: StepContext, state: StepState) -> StepState:
        self._lookup_fn = lookup_software_heritage
        if "extracted_software_heritage_archive_url" in state.data:
            return state
        state.data["extracted_software_heritage_archive_url"] = self._lookup_fn(context.repo_url)
        return state


__all__ = ["ExtractSoftwareHeritageArchivedUrlStep"]
