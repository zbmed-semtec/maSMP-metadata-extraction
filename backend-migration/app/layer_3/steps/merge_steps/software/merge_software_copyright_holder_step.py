"""Merge extracted copyright holder candidates into software metadata."""

from app.layer_1.provenance.software.defaults import CONFIDENCE_LICENSE, SOURCE_LICENSE_FILE
from app.layer_3.extraction_metadata.record import record_field_provenance
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep


class MergeSoftwareCopyrightHolderStep(ExtractionStep):
    """Merge copyright-holder candidates from any extraction source."""

    name = "software.merge_copyright_holder"

    def run(self, context: StepContext, state: StepState) -> StepState:
        copyright_holder = state.data.get("extracted_license_copyright_holder")
        if copyright_holder:
            state.metadata.copyrightHolder = copyright_holder
            record_field_provenance(state, "copyrightHolder", SOURCE_LICENSE_FILE, CONFIDENCE_LICENSE)
        return state


__all__ = ["MergeSoftwareCopyrightHolderStep"]
