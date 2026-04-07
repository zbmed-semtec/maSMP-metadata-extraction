"""Reusable API endpoint registration helpers."""

from fastapi import FastAPI

from app.api.endpoints import metadata


def register_default_endpoints(app: FastAPI) -> None:
    """
    Register the default API endpoint set.

    This is the first framework-level registrar entrypoint and preserves
    the existing endpoint contract by wiring the current metadata router.
    """
    app.include_router(metadata.router)
