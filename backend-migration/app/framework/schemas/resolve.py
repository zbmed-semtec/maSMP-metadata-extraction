"""Schema resolution helpers for registry-backed normalization and validation."""

from app.framework.schemas.plugin import SchemaPlugin
from app.framework.schemas.registry import SchemaRegistry


def resolve_schema_plugin(registry: SchemaRegistry, schema: str) -> SchemaPlugin:
    """
    Resolve and validate a schema plugin for the provided schema identifier.

    Raises:
        ValueError: when no plugin is registered for the schema.
    """
    return registry.require(schema)


def canonical_schema_name(registry: SchemaRegistry, schema: str) -> str:
    """Return canonical schema name as provided by the resolved plugin."""
    return resolve_schema_plugin(registry, schema).name
