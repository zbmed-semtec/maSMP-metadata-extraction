"""Reusable API endpoint wiring layer."""

from app.framework.api.public import assess_fairness, extract_metadata, extract_property
from app.framework.api.endpoint_config import EndpointRegistrationConfig
from app.framework.api.endpoint_registry import register_default_endpoints
from app.framework.api.metadata_router import create_metadata_router
from app.framework.api.debug_router import create_debug_router
from app.framework.api.system_router import create_system_router

__all__ = [
    "extract_metadata",
    "extract_property",
    "assess_fairness",
    "EndpointRegistrationConfig",
    "register_default_endpoints",
    "create_metadata_router",
    "create_debug_router",
    "create_system_router",
]
