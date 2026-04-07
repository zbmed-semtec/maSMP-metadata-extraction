"""Reusable API endpoint wiring layer."""

from app.framework.api.public import assess_fairness, extract_metadata, extract_property

__all__ = ["extract_metadata", "extract_property", "assess_fairness"]
