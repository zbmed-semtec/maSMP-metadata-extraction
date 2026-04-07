"""Schema plugin layer."""

from app.framework.schemas.plugin import (
    SchemaBuildContext,
    SchemaEnrichmentContext,
    SchemaPlugin,
)
from app.framework.schemas.default_plugins import MaSMPPlugin, CodeMetaPlugin
from app.framework.schemas.default_registry import create_default_schema_registry
from app.framework.schemas.registry import SchemaRegistry

__all__ = [
    "SchemaPlugin",
    "SchemaBuildContext",
    "SchemaEnrichmentContext",
    "SchemaRegistry",
    "MaSMPPlugin",
    "CodeMetaPlugin",
    "create_default_schema_registry",
]
