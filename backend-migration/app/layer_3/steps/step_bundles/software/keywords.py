"""Citation + OpenAlex keyword extract steps and merge."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.external import ExtractOpenAlexKeywordsStep
from app.layer_3.steps.extract_steps.services.files.citation import ExtractCitationKeywordsStep
from app.layer_3.steps.merge_steps.software import MergeSoftwareKeywordsStep


def software_keyword_steps(
    sources: tuple[str, ...] = ("citation", "openalex"),
) -> tuple[ExtractionStep, ...]:
    steps: list[ExtractionStep] = []
    if "citation" in sources:
        steps.append(ExtractCitationKeywordsStep())
    if "openalex" in sources:
        steps.append(ExtractOpenAlexKeywordsStep())
    steps.append(MergeSoftwareKeywordsStep())
    return tuple(steps)


__all__ = ["software_keyword_steps"]
