"""
Allowed JSON-LD keys for CodeMeta `SoftwareSourceCode` export.

Single-document CODEMETA projection from SoftwareMetadata.
"""
from typing import FrozenSet

CODEMETA_SOFTWARE_SOURCE_CODE_EXPORT_KEYS: FrozenSet[str] = frozenset({
    "name", "alternateName", "author", "version", "description", "citation",
    "codemeta:buildInstructions", "documentation", "softwareRequirements",
    "contributor", "license", "identifier", "dateCreated", "dateModified",
    "datePublished", "downloadUrl", "keywords", "codemeta:hasSourceCode",
    "releaseNotes", "codemeta:issueTracker", "programmingLanguage",
    "codemeta:developmentStatus", "codemeta:referencePublication",
    "codemeta:readme", "image", "logo", "applicationCategory", "discussionUrl",
})
