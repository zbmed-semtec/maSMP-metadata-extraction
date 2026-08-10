from typing import Any

from linkml_runtime import SchemaView
from app.layer_1.schemas.base_schema import BaseSchema

class LinkMlSchema(BaseSchema):

    def __init__(self, schema_view : SchemaView, class_name:str):
        self.schema_view = schema_view
        self.class_name = class_name

    def get_schema_name(self) -> str:
        return self.schema_view.schema.name

    def get_class_name(self)-> str:
        return self.class_name

    def get_property_list(self) -> list[str]:
        return [slot for slot in self.schema_view.class_slots(self.get_class_name())]
    
    def get_categories_of(self, property_name):
        slot = self.schema_view.get_slot(slot_name=property_name)
        if slot is None:
            return None
        return slot.categories
    
    def get_prefixes(self) -> dict[str, str]:
        return {
            obj.prefix_prefix: obj.prefix_reference for _key, obj in self.schema_view.schema.prefixes.items()
        }

    def build_context(self) -> dict[str, Any]:
        """
        Build the @context block from:
          - prefix declarations in the schema
          - slot URI annotations (resolved against prefixes)
        """
        context: dict[str, Any] = {}

        # 1. Add all declared prefixes
        context.update(self.get_prefixes())

        # 2. Map each slot name to its URI
        for slot_name, slot in self.schema_view.all_slots().items():
            uri = slot.slot_uri
            if uri:
                context[slot_name] = str(uri)

        return context

    def get_uri(self, property_name):
        slot = self.schema_view.get_slot(property_name)
        return self.schema_view.get_uri(slot, expand=True)