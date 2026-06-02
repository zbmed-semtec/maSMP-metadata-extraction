"""Extract Wayback archivedAt candidates."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.external.wayback.helpers.extract_archive import (
    WaybackClient,
)


class ExtractWaybackArchivedUrlStep(ExtractionStep):
    """Extract Wayback candidates for metadata.archivedAt."""

    name = "wayback.extract_archived_url"

    def __init__(self, client: WaybackClient | None = None) -> None:
        super().__init__()
        self.client = client or WaybackClient()

    def run(self, context: StepContext, state: StepState) -> StepState:
        if "extracted_wayback_archive_url" in state.data:
            return state
        state.data["extracted_wayback_archive_url"] = self.client.check_archive_url(context.repo_url)
        return state


__all__ = ["ExtractWaybackArchivedUrlStep"]

