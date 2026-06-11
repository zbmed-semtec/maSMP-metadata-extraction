"""Schema vocabularies by standard (`masmp/`, `codemeta/`)."""
from __future__ import annotations

from app.layer_1.schemas.codemeta import CODEMETA_SOFTWARE_SOURCE_CODE_EXPORT_KEYS
from app.layer_1.schemas.definitions import (
    SCHEMA_DEFINITIONS,
    SchemaDefinition,
    SchemaNodeDefinition,
    get_schema_definition,
)
from app.layer_1.schemas.masmp import (
    MASMP_SOFTWARE_APPLICATION_EXPORT_KEYS,
    MASMP_SOFTWARE_SOURCE_CODE_EXPORT_KEYS,
    PROFILE_CATEGORIES,
    get_category_for_key,
)

__all__ = [
    "CODEMETA_SOFTWARE_SOURCE_CODE_EXPORT_KEYS",
    "MASMP_SOFTWARE_APPLICATION_EXPORT_KEYS",
    "MASMP_SOFTWARE_SOURCE_CODE_EXPORT_KEYS",
    "PROFILE_CATEGORIES",
    "get_category_for_key",
    "SCHEMA_DEFINITIONS",
    "SchemaDefinition",
    "SchemaNodeDefinition",
    "get_schema_definition",
]
