"""Reusable API endpoint wiring layer."""

from app.framework.api.public import assess_fairness, extract_metadata, extract_property
from app.framework.api.endpoint_registry import register_default_endpoints

__all__ = [
    "extract_metadata",
    "extract_property",
    "assess_fairness",
    "register_default_endpoints",
]
