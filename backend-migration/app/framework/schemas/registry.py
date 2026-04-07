"""In-memory schema plugin registry with explicit registration APIs."""

from typing import Dict, Iterable, Optional

from app.framework.schemas.plugin import SchemaPlugin


class SchemaRegistry:
    """Stores schema plugins and resolves them by schema name."""

    def __init__(self) -> None:
        self._plugins_by_name: Dict[str, SchemaPlugin] = {}

    def register(self, plugin: SchemaPlugin) -> None:
        """Register or replace a schema plugin by its name."""
        self._plugins_by_name[plugin.name.upper()] = plugin

    def register_many(self, plugins: Iterable[SchemaPlugin]) -> None:
        """Register a collection of plugins."""
        for plugin in plugins:
            self.register(plugin)

    def get(self, schema: str) -> Optional[SchemaPlugin]:
        """Resolve a plugin for a schema, using validate fallback if needed."""
        key = schema.upper()
        direct = self._plugins_by_name.get(key)
        if direct:
            return direct

        for plugin in self._plugins_by_name.values():
            if plugin.validate(schema):
                return plugin
        return None

    def require(self, schema: str) -> SchemaPlugin:
        """Resolve a plugin for schema or raise a descriptive error."""
        plugin = self.get(schema)
        if not plugin:
            raise ValueError(f"No schema plugin registered for '{schema}'")
        return plugin

    def list_names(self) -> list[str]:
        """Return registered plugin names in stable sorted order."""
        return sorted(self._plugins_by_name.keys())
