"""Merge extracted copyright holder candidates into software metadata."""

from app.layer_1.provenance.software.defaults import CONFIDENCE_LICENSE, SOURCE_LICENSE_FILE
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin


class MergeSoftwareCopyrightHolderStep(ExtractionPlugin):
    """Merge copyright-holder candidates from any extraction source."""

    name = "software.merge_copyright_holder"
    platforms = {"gitlab", "github"}
    extracts = {'copyrightHolder'}
    priority_level = 99
    
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        copyright_holder = state.data.get("extracted_license_copyright_holder")
        if copyright_holder:
            state.metadata.copyrightHolder = copyright_holder
            record_field_provenance(state, "copyrightHolder", SOURCE_LICENSE_FILE, CONFIDENCE_LICENSE)
        return state


__all__ = ["MergeSoftwareCopyrightHolderStep"]
