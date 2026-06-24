"""Merge extracted archive URL candidates into software metadata."""

from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_ARCHIVE,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_WAYBACK,
    SOURCE_ZENODO_BADGE,
)
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin


class MergeSoftwareArchivedUrlsStep(ExtractionPlugin):
    """Merge archive URL candidates from any extraction source."""

    name = "software.merge_archived_urls"
    platforms = {"gitlab", "github"}    
    extracts = {"archivedAt"}
    priority_level = 99

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        zenodo_urls = state.data.get("extracted_zenodo_archive_urls") or []
        heritage_url = state.data.get("extracted_software_heritage_archive_url")
        wayback_url = state.data.get("extracted_wayback_archive_url")

        candidates = [*zenodo_urls, heritage_url, wayback_url]
        archived_urls = list(state.metadata.archivedAt or [])
        for url in candidates:
            if url and url not in archived_urls:
                archived_urls.append(url)
        if not archived_urls:
            return state

        state.metadata.archivedAt = archived_urls
        if zenodo_urls:
            record_field_provenance(state, "archivedAt", SOURCE_ZENODO_BADGE, CONFIDENCE_ARCHIVE)
        if heritage_url:
            record_field_provenance(
                state, "archivedAt", SOURCE_SOFTWARE_HERITAGE, CONFIDENCE_ARCHIVE
            )
        if wayback_url:
            record_field_provenance(state, "archivedAt", SOURCE_WAYBACK, CONFIDENCE_ARCHIVE)
        return state


__all__ = ["MergeSoftwareArchivedUrlsStep"]
