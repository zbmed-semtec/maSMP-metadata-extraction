"""
Response schemas for metadata endpoints (Layer 4 – API contracts).
Kept separate from routes so the API layer stays modular.
"""
from typing import Dict, Any

from pydantic import BaseModel, Field, HttpUrl


class MetadataPlainResponse(BaseModel):
    """Response for GET /metadata: canonical maSMP/CODEMETA JSON-LD only."""

    status: str
    schema_: str = Field(alias="schema", description="Schema used (maSMP or CODEMETA)")
    code_url: HttpUrl
    message: str
    results: Dict[str, Any]

    class Config:
        populate_by_name = True


class MetadataEnrichedResponse(BaseModel):
    """Response for GET /metadata/enriched: JSON-LD plus confidence, source, category per property."""

    status: str
    schema_: str = Field(alias="schema", description="Schema used (maSMP or CODEMETA)")
    code_url: HttpUrl
    message: str
    results: Dict[str, Any]
    enriched_metadata: Dict[str, Any]

    class Config:
        populate_by_name = True


class FairnessResponse(BaseModel):
    """Response for GET /fairness: JSON-LD plus FAIRness scores."""

    status: str
    schema_: str = Field(alias="schema", description="Schema used (maSMP or CODEMETA)")
    code_url: HttpUrl
    message: str
    results: Dict[str, Any]
    fairness: Dict[str, Any]

    class Config:
        populate_by_name = True
