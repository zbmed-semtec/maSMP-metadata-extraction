"""
Validation helpers for software provenance registries.

These checks protect against silent drift when developers add new fields to
SoftwareMetadata but forget to define provenance rules.
"""
from __future__ import annotations
from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_1.provenance.software.sources import (
    ALL_SOURCES,
    PROPERTY_EXTRACTION_SOURCES,
)

# SoftwareMetadata fields intentionally not tracked in provenance currently.
# Keep this explicit so omissions are deliberate and reviewable.
UNTRACKED_SOFTWARE_PROPERTIES = frozenset({
    "applicationCategory",
    "codeSampleType",
    "codemeta_buildInstructions",
    "codemeta_developmentStatus",
    "doi",
    "funders",
    "image",
    "logo",
    "masmp_deployInstructions",
    "masmp_developerDocumentation",
    "masmp_intendedUse",
    "masmp_testInstructions",
    "masmp_userDocumentation",
    "memoryRequirements",
    "operatingSystem",
    "processorRequirements",
    "releaseNotes",
    "runtimePlatform",
    "storageRequirements",
})

# Internal SoftwareMetadata fields that should never appear in provenance mapping.
INTERNAL_SOFTWARE_PROPERTIES = frozenset({"has_release"})


def validate_software_provenance_registry() -> None:
    """
    Raise ValueError when software provenance mappings are inconsistent.

    Checks:
    - every mapped property exists on SoftwareMetadata
    - every mapped source is known
    - every trackable SoftwareMetadata field is either mapped or explicitly untracked
    """
    model_fields = set(SoftwareMetadata.model_fields.keys())
    mapped_fields = set(PROPERTY_EXTRACTION_SOURCES.keys())
    trackable_fields = model_fields - INTERNAL_SOFTWARE_PROPERTIES

    unknown_mapped_fields = sorted(mapped_fields - model_fields)
    missing_mapped_fields = sorted(trackable_fields - mapped_fields - UNTRACKED_SOFTWARE_PROPERTIES)
    unknown_untracked_fields = sorted(UNTRACKED_SOFTWARE_PROPERTIES - trackable_fields)

    invalid_sources = []
    for prop, sources in PROPERTY_EXTRACTION_SOURCES.items():
        for source in sources:
            if source not in ALL_SOURCES:
                invalid_sources.append((prop, source))

    problems = []
    if unknown_mapped_fields:
        problems.append(f"unknown mapped properties: {unknown_mapped_fields}")
    if missing_mapped_fields:
        problems.append(
            "missing provenance mapping for SoftwareMetadata fields: "
            f"{missing_mapped_fields}"
        )
    if unknown_untracked_fields:
        problems.append(
            "UNTRACKED_SOFTWARE_PROPERTIES contains non-model fields: "
            f"{unknown_untracked_fields}"
        )
    if invalid_sources:
        problems.append(f"invalid sources in mapping: {invalid_sources}")

    if problems:
        raise ValueError("Software provenance registry validation failed: " + "; ".join(problems))
