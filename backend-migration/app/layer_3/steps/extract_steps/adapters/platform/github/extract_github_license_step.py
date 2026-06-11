"""GitHub license metadata steps."""
from __future__ import annotations

from app.layer_1.entities.shared_primitives import License
from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_license_payload,
)


class ExtractGithubLicenseStep:
    name = "github.extract_license"

    def run(self, context: StepContext, state: StepState) -> StepState:
        payload = github_license_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        license_info = payload.get("license") if isinstance(payload, dict) else None
        if license_info:
            metadata.license = License(name=license_info.get("name"), url=license_info.get("url"))
            if callable(record):
                record("license")
        return state


def github_license_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubLicenseStep(),)
