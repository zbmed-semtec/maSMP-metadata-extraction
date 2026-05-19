"""
Allowed JSON-LD keys per maSMP profile node when serializing SoftwareMetadata.

These are the projection filters for `maSMP:SoftwareSourceCode` and
`maSMP:SoftwareApplication` in the JSON-LD builder.
"""
from typing import FrozenSet

# Keys as emitted in JSON-LD (after codemeta_* / masmp_* → prefixed mapping).
MASMP_SOFTWARE_SOURCE_CODE_EXPORT_KEYS: FrozenSet[str] = frozenset({
    "codeRepository", "programmingLanguage", "version", "description", "name",
    "url", "maSMP:versionControlSystem", "hasSourceCode", "archivedAt",
    "author", "citation", "identifier", "keywords", "license",
    "codemeta:readme", "maSMP:intendedUse", "codeSampleType", "runtimePlatform",
    "conditionsOfAccess", "contributor", "copyrightHolder", "dateModified",
    "datePublished", "discussionUrl", "maintainer", "isAccessibleForFree",
    "codemeta:buildInstructions", "codemeta:issueTracker",
    "codemeta:referencePublication", "maSMP:developerDocumentation",
    "maSMP:learningResource", "maSMP:changelog", "maSMP:userDocumentation",
    "maSMP:deployInstructions", "maSMP:installInstructions", "maSMP:testInstructions",
    "softwareRequirements",
})

MASMP_SOFTWARE_APPLICATION_EXPORT_KEYS: FrozenSet[str] = frozenset({
    "description", "name", "url", "archivedAt", "author", "citation",
    "codemeta:readme", "maSMP:intendedUse", "releaseNotes", "softwareVersion",
    "keywords", "license", "identifier", "isAccessibleForFree",
    "maSMP:developerDocumentation", "maSMP:userDocumentation",
    "maSMP:learningResource", "codemeta:referencePublication",
    "codemeta:buildInstructions", "codemeta:issueTracker", "maSMP:changelog",
    "maSMP:deployInstructions", "maSMP:installInstructions",
    "maSMP:testInstructions", "memoryRequirements", "operatingSystem",
    "processorRequirements", "softwareRequirements", "storageRequirements",
    "conditionsOfAccess", "contributor", "copyrightHolder", "dateModified",
    "datePublished", "discussionUrl", "maintainer",
})
