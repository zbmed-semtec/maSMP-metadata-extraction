"""Default CITATION.cff step bundle."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.citation import (
    ExtractCitationAuthorsStep,
    ExtractCitationDoiStep,
    ExtractCitationKeywordsStep,
    ExtractCitationReferencePublicationStep,
    ExtractCitationTitleStep,
)
from app.layer_3.steps.merge_steps.software import (
    MergeSoftwareAlternateNamesStep,
    MergeSoftwareAuthorsStep,
    MergeSoftwareCitationEntriesStep,
    MergeSoftwareIdentifiersStep,
    MergeSoftwareKeywordsStep,
    MergeSoftwareReferencePublicationStep,
)


def default_citation_steps() -> tuple[ExtractionStep, ...]:
    return (
        ExtractCitationTitleStep(),
        ExtractCitationTitleStep(),
        ExtractCitationKeywordsStep(),
        MergeSoftwareAlternateNamesStep(),
        MergeSoftwareKeywordsStep(),
        ExtractCitationDoiStep(),
        ExtractCitationAuthorsStep(),
        MergeSoftwareAuthorsStep(),
        MergeSoftwareIdentifiersStep(),
        ExtractCitationReferencePublicationStep(),
        MergeSoftwareReferencePublicationStep(),
        MergeSoftwareCitationEntriesStep(),
    )


__all__ = ["default_citation_steps"]

