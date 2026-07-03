from app.layer_3.schemas.linkml.linkml_schema_registry import LinkMlSchemaRegistry
from linkml.validator.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
import os

_schema_registry = LinkMlSchemaRegistry()

def initialize():
    schema_dir = os.environ.get("COMET_SCHEMAS_PATH")
    if schema_dir is None:
        raise RuntimeError("COMET_SCHEMAS_PATH environment variable not set!")
    _schema_registry.load(schema_dir)

def validate(jsonld_metadata: dict, schema_name: str, schema_class: str) -> list:
    """
    Validate metadata against a schema.

    Raises:
        ValidationError if the metadata is invalid.
    """
    initialize()  # Ensure the schema registry is loaded TODO: move this to a more appropriate place, so we don't reload every time
    schema = _schema_registry.get(schema_name, schema_class)
    if not schema:
        raise ValueError(f"Schema '{schema_name}:{schema_class}' not found in registry.")

    validator = Validator(
        schema=schema.schema_view.schema,
        validation_plugins=[JsonschemaValidationPlugin(closed=True)]
    )

    metadata = {key: value for key, value in jsonld_metadata.items() if not key.startswith("@")}  # Exclude @context from validation

    errors = [
        str(r.message)
        for r in validator.iter_results(metadata, target_class=schema_class)
    ]
    return errors
