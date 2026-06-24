
from pathlib import Path
from linkml_runtime import SchemaView
from app.layer_1.schemas.base_schema_registry import BaseSchemaRegistry
from app.layer_3.schemas.linkml.linkml_schema import LinkMlSchema

class LinkMlSchemaRegistry(BaseSchemaRegistry):
    def __init__(self):
        self.schemas: dict[str, LinkMlSchema] = {}

    def load(self, directory: str | Path) -> list[str]:
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"{directory} is not a valid directory")

        loaded = []
        for path in directory.glob("*.yaml"):
            view = SchemaView(str(path))
            schema = LinkMlSchema(view, "SoftwareSourceCode")
            name = schema.get_schema_name().lower()
            self.schemas[name] = schema
            loaded.append(name)

        return loaded

    def get(self, name: str) -> LinkMlSchema:
        name = name.lower()
        if name not in self.schemas:
            raise KeyError(f"Schema '{name}' not found in registry")
        return self.schemas[name]

    def list(self) -> list[str]:
        return list(self.schemas.keys())
