"""In-memory registry for function plugins."""

from typing import Dict, Iterable, Optional

from app.framework.functions.plugin import FunctionPlugin


class FunctionRegistry:
    """Stores and resolves function plugins by plugin ID."""

    def __init__(self) -> None:
        self._plugins: Dict[str, FunctionPlugin] = {}

    def register(self, plugin: FunctionPlugin) -> None:
        """Register or replace a plugin using normalized ID."""
        self._plugins[plugin.id] = plugin

    def register_many(self, plugins: Iterable[FunctionPlugin]) -> None:
        """Register multiple plugins."""
        for plugin in plugins:
            self.register(plugin)

    def get(self, plugin_id: str) -> Optional[FunctionPlugin]:
        """Get a plugin by ID, or None if missing."""
        return self._plugins.get(plugin_id)

    def require(self, plugin_id: str) -> FunctionPlugin:
        """Get a plugin by ID or raise a descriptive error."""
        plugin = self.get(plugin_id)
        if not plugin:
            raise ValueError(f"No function plugin registered for '{plugin_id}'")
        return plugin

    def list_ids(self) -> list[str]:
        """Return registered plugin IDs in stable sorted order."""
        return sorted(self._plugins.keys())
