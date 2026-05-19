"""Citation + OpenAlex alternate-name extract steps and merge."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.external import ExtractOpenAlexAlternateNamesStep
from app.layer_3.steps.extract_steps.services.files.citation import (
    ExtractCitationTitleStep,
)
from app.layer_3.steps.merge_steps.software import MergeSoftwareAlternateNamesStep


def software_alternate_name_steps(
    sources: tuple[str, ...] = ("citation", "openalex"),
) -> tuple[ExtractionStep, ...]:
    steps: list[ExtractionStep] = []
    if "citation" in sources:
        steps.append(ExtractCitationTitleStep())
    if "openalex" in sources:
        steps.append(ExtractOpenAlexAlternateNamesStep())
    steps.append(MergeSoftwareAlternateNamesStep())
    return tuple(steps)


__all__ = ["software_alternate_name_steps"]
