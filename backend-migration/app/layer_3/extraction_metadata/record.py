"""Record per-source extraction provenance from pipeline steps."""
from __future__ import annotations

from typing import Optional

from app.layer_3.steps.contracts import StepState


def record_field_provenance(
    state: StepState,
    field: str,
    source: str,
    confidence: float,
) -> None:
    record = state.data.get("record_field")
    if callable(record):
        record(field, source=source, confidence=confidence)


def platform_source_for(context) -> str:
    from app.layer_1.provenance.software.defaults import SOURCE_GITHUB_API, SOURCE_GITLAB_API

    if context.platform == "gitlab":
        return SOURCE_GITLAB_API
    return SOURCE_GITHUB_API


__all__ = ["record_field_provenance", "platform_source_for"]
