"""Merge extracted copyright holder candidates into software metadata."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin

class MergeSoftwareCopyrightHolderStep(ExtractionPlugin):
    """Merge copyright-holder candidates from any extraction source."""

    name = "software.merge_copyright_holder"
    platforms = {"gitlab", "github"}
    extracts = {"https://schema.org/license", "https://schema.org/copyrightHolder"}
    
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        copyright_holder = state.data.get("extracted_license_copyright_holder")
        # if copyright_holder:
        #     state.metadata.copyrightHolder = copyright_holder
        #     record_field_provenance(state, "https://schema.org/copyrightHolder", SOURCE_LICENSE_FILE, CONFIDENCE_LICENSE)
        if copyright_holder:
            state.metadata_collector.collect(self.name, "https://schema.org/copyrightHolder", copyright_holder)
        return state


__all__ = ["MergeSoftwareCopyrightHolderStep"]
