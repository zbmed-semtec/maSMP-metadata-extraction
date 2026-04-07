"""Framework-level metadata router factory."""

from fastapi import APIRouter

from app.api.endpoints import metadata


def create_metadata_router() -> APIRouter:
    """
    Create router for core metadata endpoints.

    Currently wraps the existing metadata router to preserve behavior while
    standardizing framework-level router factory composition.
    """
    return metadata.router
