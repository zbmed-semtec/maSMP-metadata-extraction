"""
Build enriched_metadata for the API (per-property confidence, source, category).
Values come from results; this module only shapes annotations for the response.
"""
from typing import Dict, Any

from app.domain.schemas.masmp_profiles import get_category_for_key


def _jsonld_key_to_entity_key(jsonld_key: str) -> str:
    """Convert JSON-LD key (e.g. codemeta:readme) to entity field name (codemeta_readme)."""
    return jsonld_key.replace(":", "_")


def build_enriched_metadata(
    jsonld_document: dict,
    extraction_metadata: Dict[str, Dict[str, Any]],
    schema: str,
) -> Dict[str, Any]:
    """
    Build enriched_metadata for the API response: per-profile, per-property annotations only.
    No value (get that from results); only confidence, source, category.
    - For maSMP: per-profile (SoftwareSourceCode / SoftwareApplication), with category.
    - For CODEMETA: flat \"codemeta\" profile without categories.
    """
    # maSMP profiles
    if schema == "maSMP":
        result: Dict[str, Dict[str, Dict[str, Any]]] = {}

        for profile_key in ("maSMP:SoftwareSourceCode", "maSMP:SoftwareApplication"):
            profile_data = jsonld_document.get(profile_key)
            if not isinstance(profile_data, dict):
                continue

            result[profile_key] = {}
            skip_keys = {"@context", "@type"}

            for prop_key in profile_data.keys():
                if prop_key in skip_keys:
                    continue
                entity_key = _jsonld_key_to_entity_key(prop_key)
                record = extraction_metadata.get(entity_key, {})
                result[profile_key][prop_key] = {
                    "confidence": record.get("confidence"),
                    "source": record.get("source"),
                    "category": get_category_for_key(profile_key, prop_key),
                }

        return result

    # CODEMETA: flat profile, no category semantics (UI still shows source & confidence)
    if schema == "CODEMETA":
        result: Dict[str, Dict[str, Dict[str, Any]]] = {"codemeta": {}}
        skip_keys = {"@context", "@type"}

        for prop_key in jsonld_document.keys():
            if prop_key in skip_keys:
                continue
            entity_key = _jsonld_key_to_entity_key(prop_key)
            record = extraction_metadata.get(entity_key, {})
            result["codemeta"][prop_key] = {
                "confidence": record.get("confidence"),
                "source": record.get("source"),
                "category": None,
            }

        return result

    # Other schemas not yet annotated
    return {}
