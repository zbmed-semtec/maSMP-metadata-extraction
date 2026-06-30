from typing import AbstractSet, Any, Dict
from app.layer_1.schemas.base_schema import BaseSchema
from app.layer_1.metadata_collector.metadata_collector import MetadataCollector
from pydantic import BaseModel
from app.layer_2.use_cases.extract_metadata import JSONLDBuilder as BaseJsonLdBuilder

class JSONLDBuilder(BaseJsonLdBuilder):
    def build_jsonld(self, metadata: MetadataCollector, schema: BaseSchema) -> Dict[str, Any]:

        context = schema.build_context()
        result = {"@context": context}
        # for key, sources in metadata.data.items():
        #     for source in sources.keys():
        #         val = sources[source].property_value
        #         if isinstance(val, BaseModel):
        #             result[key] = val.model_dump()
        #         else:
        #             result[key] = val
        #         break
                
        # return result
        for property_name in schema.get_property_list():
            sources = metadata.data.get(property_name, {})
            for source in sources.keys():
                val = sources[source].property_value
                if isinstance(val, BaseModel):
                    result[property_name] = val.model_dump(mode='json')
                else:
                    result[property_name] = val
                break
        return result
    #     definition = get_schema_definition(schema.get_name())

    #     if len(definition.nodes) == 1 and definition.nodes[0].key == "__root__":
    #         node = definition.nodes[0]
    #         jsonld = {"@context": list(node.context), "@type": node.type_value}
    #         self._add_fields_to_jsonld(jsonld, metadata, node.export_keys)
    #         return jsonld

    #     document: Dict[str, Any] = {}
    #     if definition.include_has_release:
    #         document[definition.has_release_key] = has_release

    #     for node in definition.nodes:
    #         payload = {"@context": list(node.context), "@type": node.type_value}
    #         self._add_fields_to_jsonld(payload, metadata, node.export_keys)
    #         document[node.key] = payload
    #     return document

    # def _add_fields_to_jsonld(self, jsonld: Dict[str, Any], metadata: SoftwareMetadata, allowed_fields: AbstractSet[str]) -> None:
    #     metadata_dict = metadata.model_dump(exclude_none=True, exclude={"has_release"}, by_alias=True)
    #     for key, value in metadata_dict.items():
    #         if key.startswith("codemeta_"):
    #             jsonld_key = key.replace("_", ":", 1)
    #         elif key.startswith("masmp_"):
    #             jsonld_key = "maSMP:" + key[len("masmp_"):]
    #         else:
    #             jsonld_key = key
    #         if jsonld_key in allowed_fields or key in allowed_fields:
    #             if isinstance(value, list) and not value:
    #                 continue
    #             jsonld[jsonld_key] = value


__all__ = ["JSONLDBuilder"]
