"""Factory for default first-party schema plugin registry."""

from app.framework.schemas.default_plugins import CodeMetaPlugin, MaSMPPlugin
from app.framework.schemas.registry import SchemaRegistry


def create_default_schema_registry() -> SchemaRegistry:
    """Return registry preloaded with built-in maSMP and CODEMETA plugins."""
    registry = SchemaRegistry()
    registry.register_many([MaSMPPlugin(), CodeMetaPlugin()])
    return registry
