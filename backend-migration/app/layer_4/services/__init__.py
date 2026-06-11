"""API-level services (composition / wiring)."""
from __future__ import annotations
from app.layer_4.services.metadata_service import run_extraction

__all__ = ["run_extraction"]
