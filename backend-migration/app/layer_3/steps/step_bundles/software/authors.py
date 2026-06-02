"""Citation + README + OpenAlex author extract steps and merge."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.external import ExtractOpenAlexAuthorsStep
from app.layer_3.steps.extract_steps.services.files.citation import ExtractCitationAuthorsStep
from app.layer_3.steps.extract_steps.services.files.readme import ExtractReadmeBibtexStep
from app.layer_3.steps.merge_steps.software import MergeSoftwareAuthorsStep


def software_author_steps(
    sources: tuple[str, ...] = ("citation", "readme", "openalex"),
) -> tuple[ExtractionStep, ...]:
    steps: list[ExtractionStep] = []
    if "citation" in sources:
        steps.append(ExtractCitationAuthorsStep())
    if "readme" in sources:
        steps.append(ExtractReadmeBibtexStep())
    if "openalex" in sources:
        steps.append(ExtractOpenAlexAuthorsStep())
    steps.append(MergeSoftwareAuthorsStep())
    return tuple(steps)


__all__ = ["software_author_steps"]
