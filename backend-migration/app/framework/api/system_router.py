"""Framework-level system router factory."""

from fastapi import APIRouter


def create_system_router() -> APIRouter:
    """Create router for lightweight system/info endpoints."""
    router = APIRouter(prefix="/api", tags=["Metadata"])

    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "metadata-extractor"}

    @router.get("/platforms")
    async def get_supported_platforms():
        """Get list of supported platforms."""
        return {
            "platforms": [
                {"name": "GitHub", "url_pattern": "github.com", "description": "GitHub repositories"},
                {"name": "GitLab", "url_pattern": "gitlab.com", "description": "GitLab repositories"},
            ]
        }

    return router
