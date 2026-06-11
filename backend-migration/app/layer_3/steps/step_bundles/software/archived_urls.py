"""External archived-URL extract steps and merge."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.external import (
    ExtractSoftwareHeritageArchivedUrlStep,
    ExtractWaybackArchivedUrlStep,
    ExtractZenodoArchivedUrlsStep,
)
from app.layer_3.steps.merge_steps.software import MergeSoftwareArchivedUrlsStep


def software_archived_url_steps(
    sources: tuple[str, ...] = ("zenodo", "software_heritage", "wayback"),
) -> tuple[ExtractionStep, ...]:
    steps: list[ExtractionStep] = []
    if "zenodo" in sources:
        steps.append(ExtractZenodoArchivedUrlsStep())
    if "software_heritage" in sources:
        steps.append(ExtractSoftwareHeritageArchivedUrlStep())
    if "wayback" in sources:
        steps.append(ExtractWaybackArchivedUrlStep())
    steps.append(MergeSoftwareArchivedUrlsStep())
    return tuple(steps)


__all__ = ["software_archived_url_steps"]
