from __future__ import annotations
from typing import AbstractSet, Any, Dict

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_1.schemas import get_schema_definition

class JSONLDBuilder:
    def build_jsonld(self, metadata: SoftwareMetadata, schema: str, has_release: bool) -> Dict[str, Any]:
        definition = get_schema_definition(schema)

        if len(definition.nodes) == 1 and definition.nodes[0].key == "__root__":
            node = definition.nodes[0]
            jsonld = {"@context": list(node.context), "@type": node.type_value}
            self._add_fields_to_jsonld(jsonld, metadata, node.export_keys)
            return jsonld

        document: Dict[str, Any] = {}
        if definition.include_has_release:
            document[definition.has_release_key] = has_release

        for node in definition.nodes:
            payload = {"@context": list(node.context), "@type": node.type_value}
            self._add_fields_to_jsonld(payload, metadata, node.export_keys)
            document[node.key] = payload
        return document

    def _add_fields_to_jsonld(self, jsonld: Dict[str, Any], metadata: SoftwareMetadata, allowed_fields: AbstractSet[str]) -> None:
        metadata_dict = metadata.model_dump(exclude_none=True, exclude={"has_release"}, by_alias=True)
        for key, value in metadata_dict.items():
            if key.startswith("codemeta_"):
                jsonld_key = key.replace("_", ":", 1)
            elif key.startswith("masmp_"):
                jsonld_key = "maSMP:" + key[len("masmp_"):]
            else:
                jsonld_key = key
            if jsonld_key in allowed_fields or key in allowed_fields:
                if isinstance(value, list) and not value:
                    continue
                jsonld[jsonld_key] = value


__all__ = ["JSONLDBuilder"]
