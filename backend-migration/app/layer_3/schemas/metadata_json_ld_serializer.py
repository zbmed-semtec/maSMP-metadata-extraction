import json
from pathlib import Path
from dataclasses import dataclass, field
from linkml_runtime.utils.schemaview import SchemaView
from app.layer_1.schemas.metadata_record import MetadataRecord

class MetadataJsonLdSerializer:
    def __init__(self, registry):
        self.registry = registry

    def to_jsonld(self, record: MetadataRecord) -> str:
        view: SchemaView = self.registry.get(record.schema_name)
        context = self._build_context(view, record.class_name)
        doc = {"@context": context, "@type": record.class_name, **record.data}
        return json.dumps(doc, indent=2)

    def from_jsonld(self, json_str: str) -> MetadataRecord:
        doc = json.loads(json_str)
        # Extract schema name from @context if present
        context = doc.get("@context", {})
        schema_name = context.get("@schema")
        class_name = doc.get("@type")

        data = {k: v for k, v in doc.items() if not k.startswith("@")}
        return MetadataRecord(schema_name=schema_name, class_name=class_name, data=data)

    def _build_context(self, view: SchemaView, class_name: str) -> dict:
        schema = view.schema
        context = {
            "@schema": schema.name,  # custom key to allow round-tripping
        }

        # Add schema-level prefix if defined
        if schema.id:
            context["@vocab"] = str(schema.id) + "/"

        # Add slot URIs for slots used by this class
        induced = view.get_class(class_name)
        if induced:
            for slot_name in view.all_slots():
                slot = view.get_slot(slot_name)
                if slot and slot.slot_uri:
                    context[slot_name] = str(slot.slot_uri)

        return context
