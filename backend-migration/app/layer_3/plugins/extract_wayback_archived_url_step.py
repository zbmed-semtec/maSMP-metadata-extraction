"""Extract Wayback archivedAt candidates."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.wayback.helpers.extract_archive import (
    WaybackClient,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractWaybackArchivedUrlStep(ExtractionPlugin):
    """Extract Wayback candidates for metadata.archivedAt."""

    name = "wayback.extract_archived_url"
    platforms = {"gitlab", "github"}
    extracts = {"archivedAt"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        self.client = WaybackClient()
        if "extracted_wayback_archive_url" in state.data:
            return state
        state.data["extracted_wayback_archive_url"] = self.client.check_archive_url(context.repo_url)
        return state

__all__ = ["ExtractWaybackArchivedUrlStep"]

