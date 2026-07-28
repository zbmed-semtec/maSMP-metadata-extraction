"""
Software-domain mapping: each metadata property -> extraction sources.

This registry is intentionally domain-scoped. If you add another domain,
create a sibling package (e.g. `provenance/training`) rather than extending this.
"""
from __future__ import annotations
from app.layer_1.provenance.software.defaults import (
    SOURCE_CITATION_CFF,
    SOURCE_GITHUB_API,
    SOURCE_GITLAB_API,
    SOURCE_LICENSE_FILE,
    SOURCE_LLM,
    SOURCE_OPENALEX,
    SOURCE_README_PARSER,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_WAYBACK,
    SOURCE_ZENODO_BADGE,
)

# Property (SoftwareMetadata field name) -> source identifiers that can set it
PROPERTY_EXTRACTION_SOURCES: dict[str, tuple[str, ...]] = {
    # Platform API (GitHub / GitLab)
    "name": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "description": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "documentation": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_README_PARSER, SOURCE_LLM),
    "url": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "codeRepository": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "dateCreated": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "dateModified": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "datePublished": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "conditionsOfAccess": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "isAccessibleForFree": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "issueTracker": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "codemeta_issueTracker": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "discussionUrl": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "downloadUrl": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "hasSourceCode": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "codemeta_hasSourceCode": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "keywords": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_CITATION_CFF, SOURCE_OPENALEX),
    "masmp_versionControlSystem": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "programmingLanguage": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "contributor": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "license": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_README_PARSER, SOURCE_LLM),
    "codemeta_readme": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_README_PARSER),
    "masmp_changelog": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "softwareVersion": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "version": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "softwareRequirements": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    # File parsing: CITATION.cff
    "alternateName": (SOURCE_CITATION_CFF, SOURCE_OPENALEX, SOURCE_LLM),
    "author": (SOURCE_CITATION_CFF, SOURCE_README_PARSER, SOURCE_OPENALEX, SOURCE_LLM),
    "contributor": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_LLM),
    "codemeta_referencePublication": (
        SOURCE_CITATION_CFF,
        SOURCE_README_PARSER,
        SOURCE_OPENALEX,
        SOURCE_LLM,
    ),
    "citation": (SOURCE_CITATION_CFF, SOURCE_README_PARSER, SOURCE_LLM),
    "identifier": (SOURCE_CITATION_CFF, SOURCE_README_PARSER, SOURCE_LLM),
    # File parsing: LICENSE
    "copyrightHolder": (SOURCE_LICENSE_FILE, SOURCE_LLM),
    "maintainer": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_LLM),
    "masmp_installInstructions": (SOURCE_README_PARSER, SOURCE_LLM),
    "masmp_learningResource": (SOURCE_README_PARSER, SOURCE_LLM),
    # External: Zenodo / Wayback / Software Heritage
    "archivedAt": (SOURCE_ZENODO_BADGE, SOURCE_WAYBACK, SOURCE_SOFTWARE_HERITAGE),
}

# Properties that accept contributions from multiple sources (merge, don't overwrite)
MULTI_SOURCE_PROPERTIES = frozenset({
    "keywords",
    "identifier",
    "alternateName",
    "author",
    "archivedAt",
    "codemeta_referencePublication",
})

# All sources that appear in the registry
ALL_SOURCES = {
    SOURCE_GITHUB_API,
    SOURCE_GITLAB_API,
    SOURCE_CITATION_CFF,
    SOURCE_LICENSE_FILE,
    SOURCE_README_PARSER,
    SOURCE_ZENODO_BADGE,
    SOURCE_WAYBACK,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_OPENALEX,
    SOURCE_LLM,
}


def get_sources_for_property(property_name: str) -> tuple[str, ...]:
    """Return the extraction sources that can set the given software property."""
    return PROPERTY_EXTRACTION_SOURCES.get(property_name, ())


def get_properties_for_source(source: str) -> list[str]:
    """Return all software properties that can be set by the given source."""
    return [
        prop for prop, sources in PROPERTY_EXTRACTION_SOURCES.items()
        if source in sources
    ]
