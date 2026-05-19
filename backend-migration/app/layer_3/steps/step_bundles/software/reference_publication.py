"""Citation + README + OpenAlex reference-publication extract steps and merges."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.external import ExtractOpenAlexReferencePublicationStep
from app.layer_3.steps.extract_steps.services.files.citation import (
    ExtractCitationReferencePublicationStep,
)
from app.layer_3.steps.extract_steps.services.files.readme import ExtractReadmeBibtexStep
from app.layer_3.steps.merge_steps.software import (
    MergeSoftwareCitationEntriesStep,
    MergeSoftwareReferencePublicationStep,
)


def software_reference_publication_steps(
    sources: tuple[str, ...] = ("citation", "readme", "openalex"),
) -> tuple[ExtractionStep, ...]:
    steps: list[ExtractionStep] = []
    if "citation" in sources:
        steps.append(ExtractCitationReferencePublicationStep())
    if "readme" in sources:
        steps.append(ExtractReadmeBibtexStep())
    if "openalex" in sources:
        steps.append(ExtractOpenAlexReferencePublicationStep())
    steps.append(MergeSoftwareReferencePublicationStep())
    steps.append(MergeSoftwareCitationEntriesStep())
    return tuple(steps)


__all__ = ["software_reference_publication_steps"]
