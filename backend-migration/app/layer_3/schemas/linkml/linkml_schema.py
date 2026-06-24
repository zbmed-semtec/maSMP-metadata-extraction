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