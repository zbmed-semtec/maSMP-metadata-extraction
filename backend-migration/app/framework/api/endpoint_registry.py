"""Reusable API endpoint registration helpers."""

from fastapi import FastAPI

from app.framework.api.debug_router import create_debug_router
from app.framework.api.endpoint_config import EndpointRegistrationConfig
from app.framework.api.metadata_router import create_metadata_router
from app.framework.api.system_router import create_system_router


def register_default_endpoints(
    app: FastAPI,
    config: EndpointRegistrationConfig | None = None,
) -> None:
    """
    Register the default API endpoint set.

    This is the first framework-level registrar entrypoint and preserves
    the existing endpoint contract by wiring the current metadata router.
    """
    config = config or EndpointRegistrationConfig()
    if config.include_metadata:
        app.include_router(create_metadata_router())
    if config.include_debug:
        app.include_router(create_debug_router())
    if config.include_system:
        app.include_router(create_system_router())
