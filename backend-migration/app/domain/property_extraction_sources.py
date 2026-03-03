"""
Canonical mapping: each metadata property → list of extraction sources that can set it.

Used for:
- Documentation: which sources contribute to which property
- Tests: assert each property flows through its expected sources and adapters
         only record (property, source) pairs that are in this registry
"""
from app.domain.extraction_sources import (
    SOURCE_GITHUB_API,
    SOURCE_GITLAB_API,
    SOURCE_CITATION_CFF,
    SOURCE_LICENSE_FILE,
    SOURCE_README_PARSER,
    SOURCE_ZENODO_BADGE,
    SOURCE_WAYBACK,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_OPENALEX,
)

# Property (entity field name) -> tuple of source identifiers that can set it
PROPERTY_EXTRACTION_SOURCES: dict[str, tuple[str, ...]] = {
    # Platform API (GitHub / GitLab)
    "name": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "description": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
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
    "license": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "codemeta_readme": (SOURCE_GITHUB_API, SOURCE_GITLAB_API, SOURCE_README_PARSER),
    "masmp_changelog": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "softwareVersion": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    "version": (SOURCE_GITHUB_API, SOURCE_GITLAB_API),
    # File parsing: CITATION.cff
    "alternateName": (SOURCE_CITATION_CFF, SOURCE_OPENALEX),
    "author": (SOURCE_CITATION_CFF, SOURCE_README_PARSER, SOURCE_OPENALEX),
    "codemeta_referencePublication": (
        SOURCE_CITATION_CFF,
        SOURCE_README_PARSER,
        SOURCE_OPENALEX,
    ),
    "citation": (SOURCE_CITATION_CFF,),
    "identifier": (SOURCE_CITATION_CFF, SOURCE_README_PARSER),
    # File parsing: LICENSE
    "copyrightHolder": (SOURCE_LICENSE_FILE,),
    # File parsing: README (parser)
    # codemeta_readme, author, codemeta_referencePublication already listed above
    # External: Zenodo / Wayback
    "archivedAt": (SOURCE_ZENODO_BADGE, SOURCE_WAYBACK, SOURCE_SOFTWARE_HERITAGE),
    # External: OpenAlex
    # alternateName, author, keywords, codemeta_referencePublication already listed above
}

# Properties that accept contributions from multiple sources (merge, don't overwrite).
# Each source is hit; new values are merged (e.g. keywords, identifier, alternateName, author, archivedAt).
# Extraction metadata stores multiple (source, confidence) and aggregates confidence.
MULTI_SOURCE_PROPERTIES = frozenset({"keywords", "identifier", "alternateName", "author", "archivedAt"})

# All sources that appear in the registry (for validation)
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
}


def get_sources_for_property(property_name: str) -> tuple[str, ...]:
    """Return the list of extraction sources that can set the given property."""
    return PROPERTY_EXTRACTION_SOURCES.get(property_name, ())


def get_properties_for_source(source: str) -> list[str]:
    """Return all properties that can be set by the given source."""
    return [
        prop for prop, sources in PROPERTY_EXTRACTION_SOURCES.items()
        if source in sources
    ]
