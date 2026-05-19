"""
Research-software domain model: everything extractors fill before JSON-LD export.

This is the internal \"worksheet\" for the software pipeline only.
Other domains (e.g. training materials) should get their own package under `entities/`.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

from app.layer_1.entities.shared_primitives.types import (
    License,
    ReferencePublication,
    VersionControlSystem,
)


class SoftwareMetadata(BaseModel):
    """
    Canonical model for **research software** extracted from repos (GitHub, GitLab, …).

    Vocabulary-specific output (maSMP, CodeMeta, …) is produced later by projecting
    this object — see `layer_1/schemas/` and `JSONLDBuilder`.
    """

    # Basic Information
    name: Optional[str] = None
    alternateName: Optional[List[str]] = None
    description: Optional[str] = None
    version: Optional[str] = None
    softwareVersion: Optional[str] = None

    # Repository Information
    codeRepository: Optional[str] = None
    url: Optional[HttpUrl] = None
    downloadUrl: Optional[HttpUrl] = None
    hasSourceCode: Optional[str] = None
    codemeta_hasSourceCode: Optional[str] = None

    # People
    author: Optional[List[Dict[str, Any]]] = None
    contributor: Optional[List[Dict[str, Any]]] = None
    maintainer: Optional[List[Dict[str, Any]]] = None
    copyrightHolder: Optional[str] = None

    # Dates
    dateCreated: Optional[str] = None
    dateModified: Optional[str] = None
    datePublished: Optional[str] = None

    # Technical Details
    programmingLanguage: Optional[List[str]] = None
    runtimePlatform: Optional[List[str]] = None
    operatingSystem: Optional[List[str]] = None
    softwareRequirements: Optional[List[str]] = None
    memoryRequirements: Optional[str] = None
    processorRequirements: Optional[str] = None
    storageRequirements: Optional[str] = None

    # License & Access
    license: Optional[License] = None
    isAccessibleForFree: Optional[str] = None
    conditionsOfAccess: Optional[str] = None

    # Documentation & Resources
    documentation: Optional[HttpUrl] = None
    codemeta_readme: Optional[str] = None
    codemeta_buildInstructions: Optional[str] = None
    masmp_developerDocumentation: Optional[str] = None
    masmp_userDocumentation: Optional[str] = None
    masmp_learningResource: Optional[str] = None
    masmp_installInstructions: Optional[str] = None
    masmp_deployInstructions: Optional[str] = None
    masmp_testInstructions: Optional[str] = None
    masmp_changelog: Optional[str] = None

    # Metadata
    identifier: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    citation: Optional[List[Dict[str, Any]]] = None
    codemeta_referencePublication: Optional[ReferencePublication] = None

    # Version Control
    masmp_versionControlSystem: Optional[VersionControlSystem] = None

    # Issue Tracking & Discussion
    issueTracker: Optional[HttpUrl] = None
    codemeta_issueTracker: Optional[HttpUrl] = None
    discussionUrl: Optional[HttpUrl] = None

    # Release Information
    releaseNotes: Optional[str] = None
    codemeta_developmentStatus: Optional[str] = None

    # Archive Information
    archivedAt: Optional[List[str]] = None

    # Additional maSMP fields
    masmp_intendedUse: Optional[str] = None
    codeSampleType: Optional[str] = None
    applicationCategory: Optional[str] = None

    # Media
    image: Optional[HttpUrl] = None
    logo: Optional[HttpUrl] = None

    # Additional fields that may come from external sources
    funders: Optional[List[Dict[str, Any]]] = None
    doi: Optional[str] = None

    # Internal flag for release status (not part of final JSON-LD)
    has_release: bool = False

    class Config:
        populate_by_name = True
        extra = "allow"
        validate_assignment = True


# Backward-compatible name used across adapters and tests
RepositoryMetadata = SoftwareMetadata
