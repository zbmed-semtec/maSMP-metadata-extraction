"""Factory for default first-party function plugin registry."""

from app.framework.functions.default_plugins import (
    ExternalEnrichmentPlugin,
    FileParsingPlugin,
    LLMEnrichmentPlugin,
    PlatformExtractionPlugin,
    SchemaBuildPlugin,
)
from app.framework.functions.registry import FunctionRegistry


def create_default_function_registry() -> FunctionRegistry:
    """Return registry preloaded with default 5-stage extraction plugins."""
    registry = FunctionRegistry()
    registry.register_many(
        [
            PlatformExtractionPlugin(),
            FileParsingPlugin(),
            ExternalEnrichmentPlugin(),
            LLMEnrichmentPlugin(),
            SchemaBuildPlugin(),
        ]
    )
    return registry
