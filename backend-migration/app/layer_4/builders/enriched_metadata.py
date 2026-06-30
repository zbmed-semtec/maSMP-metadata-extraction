"""
Build enriched_metadata for the API (per-property confidence, source, category).
Values come from results; this module only shapes annotations for the response.
"""
from typing import Dict, Any

from app.layer_1.schemas.masmp.profiles import get_category_for_key
from app.layer_1.schemas.base_schema import BaseSchema
from app.layer_1.metadata_collector.metadata_collector import MetadataCollector, MetadataProperty


def _jsonld_key_to_entity_key(jsonld_key: str) -> str:
    """Convert JSON-LD key (e.g. codemeta:readme, maSMP:versionControlSystem) to entity field name."""
    # Codemeta keys: codemeta:readme -> codemeta_readme
    if jsonld_key.startswith("codemeta:"):
        return jsonld_key.replace(":", "_", 1)
    # maSMP keys: maSMP:versionControlSystem -> masmp_versionControlSystem
    if jsonld_key.startswith("maSMP:"):
        return "masmp_" + jsonld_key.split(":", 1)[1]
    # Fallback: simple colon-to-underscore mapping
    return jsonld_key.replace(":", "_")


def build_enriched_metadata(
    collector: MetadataCollector,
    schema: BaseSchema,
) -> Dict[str, Any]:
    """
    Build enriched_metadata for the API response: per-profile, per-property annotations only.
    No value (get that from results); only confidence, source, category.
    - For maSMP: per-profile (SoftwareSourceCode / SoftwareApplication), with category.
    - For CODEMETA: flat \"codemeta\" profile without category.
    """
    # # maSMP profiles
    # if schema == "maSMP":
    #     result: Dict[str, Dict[str, Dict[str, Any]]] = {}

    #     for profile_key in ("maSMP:SoftwareSourceCode", "maSMP:SoftwareApplication"):
    #         profile_data = jsonld_document.get(profile_key)
    #         if not isinstance(profile_data, dict):
    #             continue

    #         result[profile_key] = {}
    #         skip_keys = {"@context", "@type"}

    #         for prop_key in profile_data.keys():
    #             if prop_key in skip_keys:
    #                 continue
    #             entity_key = _jsonld_key_to_entity_key(prop_key)
    #             record = extraction_metadata.get(entity_key, {})

    #             # Default source/confidence from extraction metadata
    #             source = record.get("source")
    #             confidence = record.get("confidence")

    #             # Version control system is a constant, schema-level recommendation
    #             # rather than something inferred from external data.
    #             if prop_key == "maSMP:versionControlSystem":
    #                 source = "Constant"
    #                 confidence = 1.0

    #             result[profile_key][prop_key] = {
    #                 "confidence": confidence,
    #                 "source": source,
    #                 "category": get_category_for_key(profile_key, prop_key),
    #             }

    #     return result

    # # CODEMETA: flat profile, no category semantics (UI still shows source & confidence)
    # if schema == "CODEMETA":
    #     result: Dict[str, Dict[str, Dict[str, Any]]] = {"codemeta": {}}
    #     skip_keys = {"@context", "@type"}

    #     for prop_key in jsonld_document.keys():
    #         if prop_key in skip_keys:
    #             continue
    #         entity_key = _jsonld_key_to_entity_key(prop_key)
    #         record = extraction_metadata.get(entity_key, {})
    #         result["codemeta"][prop_key] = {
    #             "confidence": record.get("confidence"),
    #             "source": record.get("source"),
    #             "category": None,
    #         }

    #     return result

    result = {}
    for prop in schema.get_property_list():
        for record in collector.get(prop).values():
            record : MetadataProperty = record
            category = schema.get_categories_of(property_name=record.property_name)
            if isinstance(category, list):
                if len(category) > 0:
                    category = category[0]
                else:
                    category = "optional"
            if category is None:
                category = "optional"
            result[prop] = {
                "confidence": record.confidence,
                "source": record.source,
                "category": category,
            }

    # Other schemas not yet annotated
    return result
