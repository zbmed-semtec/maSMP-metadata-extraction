"""Default README step bundle."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.readme import (
    ExtractReadmeBibtexStep,
    ExtractReadmeIdentifierStep,
)
from app.layer_3.steps.merge_steps.software import (
    MergeSoftwareAuthorsStep,
    MergeSoftwareIdentifiersStep,
    MergeSoftwareReferencePublicationStep,
)


def default_readme_steps() -> tuple[ExtractionStep, ...]:
    return (
        ExtractReadmeIdentifierStep(),
        MergeSoftwareIdentifiersStep(),
        ExtractReadmeBibtexStep(),
        MergeSoftwareReferencePublicationStep(),
        MergeSoftwareAuthorsStep(),
    )


__all__ = ["default_readme_steps"]

