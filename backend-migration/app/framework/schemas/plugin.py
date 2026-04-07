"""Schema plugin contract and lightweight context objects."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol


@dataclass(frozen=True)
class SchemaBuildContext:
    """Inputs needed by schema plugins to build output payloads."""

    metadata: Any
    has_release: bool
    raw_schema: str


@dataclass(frozen=True)
class SchemaEnrichmentContext:
    """Optional enrichment inputs for schema-specific metadata augmentation."""

    jsonld_document: Dict[str, Any]
    extraction_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    raw_schema: Optional[str] = None


class SchemaPlugin(Protocol):
    """Contract for schema-specific build and optional enrichment behavior."""

    name: str

    def validate(self, schema: str) -> bool:
        """Return True if this plugin handles the provided schema identifier."""
        ...

    def build_output(self, context: SchemaBuildContext) -> Dict[str, Any]:
        """Build schema-specific output from normalized metadata."""
        ...

    def enrich_output(self, context: SchemaEnrichmentContext) -> Dict[str, Any]:
        """
        Optionally enrich output metadata.

        Implementations may return an empty dictionary when enrichment is not used.
        """
        ...
