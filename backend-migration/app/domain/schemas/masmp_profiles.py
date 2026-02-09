"""
maSMP profile property categories (required / recommended / optional).
Keys match JSON-LD output (e.g. masmp:versionControlSystem, codemeta:readme).
"""
from typing import Dict, List

# Required and recommended property names per profile (as in JSON-LD)
MASMP_SOFTWARE_SOURCE_CODE: Dict[str, List[str]] = {
    "required": [
        "name",
        "description",
        "url",
        "codeRepository",
        "version",
        "programmingLanguage",
    ],
    "recommended": [
        "author",
        "citation",
        "license",
        "identifier",
        "keywords",
        "codemeta:readme",
        "masmp:versionControlSystem",
        "masmp:intendedUse",
        "archivedAt",
    ],
}

MASMP_SOFTWARE_APPLICATION: Dict[str, List[str]] = {
    "required": ["name", "description", "url"],
    "recommended": [
        "author",
        "citation",
        "license",
        "identifier",
        "keywords",
        "releaseNotes",
        "codemeta:readme",
        "archivedAt",
        "masmp:intendedUse",
        "softwareVersion",
    ],
}

PROFILE_CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "maSMP:SoftwareSourceCode": MASMP_SOFTWARE_SOURCE_CODE,
    "maSMP:SoftwareApplication": MASMP_SOFTWARE_APPLICATION,
}


def get_category_for_key(profile_key: str, prop_key: str) -> str:
    """Return 'required', 'recommended', or 'optional' for a property in a profile."""
    categories = PROFILE_CATEGORIES.get(profile_key)
    if not categories:
        return "optional"
    if prop_key in categories.get("required", []):
        return "required"
    if prop_key in categories.get("recommended", []):
        return "recommended"
    return "optional"
