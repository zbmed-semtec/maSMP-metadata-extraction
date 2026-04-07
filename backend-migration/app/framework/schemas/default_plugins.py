"""First-party schema plugins that preserve current maSMP/CODEMETA behavior."""

from typing import Any, Dict

from app.adapters.jsonld_builder import JSONLDBuilder
from app.api.builders.enriched_metadata import build_enriched_metadata
from app.framework.schemas.plugin import (
    SchemaBuildContext,
    SchemaEnrichmentContext,
    SchemaPlugin,
)


class _BaseBuilderSchemaPlugin:
    """Shared adapter around the existing JSONLDBuilder implementation."""

    name: str
    _schema_key: str

    def __init__(self) -> None:
        self._builder = JSONLDBuilder()

    def validate(self, schema: str) -> bool:
        return schema.upper() == self._schema_key

    def build_output(self, context: SchemaBuildContext) -> Dict[str, Any]:
        return self._builder.build_jsonld(
            metadata=context.metadata,
            schema=self.name,
            has_release=context.has_release,
        )

    def enrich_output(self, context: SchemaEnrichmentContext) -> Dict[str, Any]:
        return build_enriched_metadata(
            jsonld_document=context.jsonld_document,
            extraction_metadata=context.extraction_metadata,
            schema=self.name,
        )


class MaSMPPlugin(_BaseBuilderSchemaPlugin, SchemaPlugin):
    """Schema plugin for maSMP outputs."""

    name = "maSMP"
    _schema_key = "MASMP"


class CodeMetaPlugin(_BaseBuilderSchemaPlugin, SchemaPlugin):
    """Schema plugin for CODEMETA outputs."""

    name = "CODEMETA"
    _schema_key = "CODEMETA"
