"""Extraction steps backed by external enrichment services."""
from __future__ import annotations

from app.layer_3.steps.extract_steps.services.external.openalex import (
    ExtractOpenAlexAlternateNamesStep,
    ExtractOpenAlexAuthorsStep,
    ExtractOpenAlexKeywordsStep,
    ExtractOpenAlexReferencePublicationStep,
)
from app.layer_3.steps.extract_steps.services.external.software_heritage import (
    ExtractSoftwareHeritageArchivedUrlStep,
)
from app.layer_3.steps.extract_steps.services.external.wayback import ExtractWaybackArchivedUrlStep
from app.layer_3.steps.extract_steps.services.external.zenodo import ExtractZenodoArchivedUrlsStep

__all__ = [
    "ExtractOpenAlexAlternateNamesStep",
    "ExtractOpenAlexAuthorsStep",
    "ExtractOpenAlexKeywordsStep",
    "ExtractOpenAlexReferencePublicationStep",
    "ExtractSoftwareHeritageArchivedUrlStep",
    "ExtractWaybackArchivedUrlStep",
    "ExtractZenodoArchivedUrlsStep",
]

