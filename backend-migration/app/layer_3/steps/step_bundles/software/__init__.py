"""Per-property software pipeline fragments (extract + merge)."""
from __future__ import annotations

from app.layer_3.steps.step_bundles.software.alternate_names import software_alternate_name_steps
from app.layer_3.steps.step_bundles.software.archived_urls import software_archived_url_steps
from app.layer_3.steps.step_bundles.software.authors import software_author_steps
from app.layer_3.steps.step_bundles.software.identifiers import software_identifier_steps
from app.layer_3.steps.step_bundles.software.keywords import software_keyword_steps
from app.layer_3.steps.step_bundles.software.reference_publication import (
    software_reference_publication_steps,
)

__all__ = [
    "software_alternate_name_steps",
    "software_archived_url_steps",
    "software_author_steps",
    "software_identifier_steps",
    "software_keyword_steps",
    "software_reference_publication_steps",
]
