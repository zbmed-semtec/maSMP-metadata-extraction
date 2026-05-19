"""Citation + README identifier extract steps and merge."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.citation import ExtractCitationDoiStep
from app.layer_3.steps.extract_steps.services.files.readme import ExtractReadmeIdentifierStep
from app.layer_3.steps.merge_steps.software import MergeSoftwareIdentifiersStep


def software_identifier_steps(
    sources: tuple[str, ...] = ("citation", "readme"),
) -> tuple[ExtractionStep, ...]:
    steps: list[ExtractionStep] = []
    if "citation" in sources:
        steps.append(ExtractCitationDoiStep())
    if "readme" in sources:
        steps.append(ExtractReadmeIdentifierStep())
    steps.append(MergeSoftwareIdentifiersStep())
    return tuple(steps)


__all__ = ["software_identifier_steps"]
