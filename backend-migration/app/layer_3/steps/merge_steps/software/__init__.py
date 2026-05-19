"""Property-specific merge steps for software metadata."""

from app.layer_3.steps.merge_steps.software.merge_software_alternate_names_step import (
    MergeSoftwareAlternateNamesStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_authors_step import (
    MergeSoftwareAuthorsStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_archived_urls_step import (
    MergeSoftwareArchivedUrlsStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_citation_entries_step import (
    MergeSoftwareCitationEntriesStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_copyright_holder_step import (
    MergeSoftwareCopyrightHolderStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_identifiers_step import (
    MergeSoftwareIdentifiersStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_keywords_step import (
    MergeSoftwareKeywordsStep,
)
from app.layer_3.steps.merge_steps.software.merge_software_reference_publication_step import (
    MergeSoftwareReferencePublicationStep,
)

__all__ = [
    "MergeSoftwareAlternateNamesStep",
    "MergeSoftwareArchivedUrlsStep",
    "MergeSoftwareAuthorsStep",
    "MergeSoftwareCitationEntriesStep",
    "MergeSoftwareCopyrightHolderStep",
    "MergeSoftwareIdentifiersStep",
    "MergeSoftwareKeywordsStep",
    "MergeSoftwareReferencePublicationStep",
]

