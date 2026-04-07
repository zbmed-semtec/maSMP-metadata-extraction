"""Framework-level debug router factory."""

import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import HttpUrl

from app.api.services.metadata_service import compare_legacy_and_pipeline_extraction


def _parity_endpoint_enabled() -> bool:
    raw = os.getenv("COMET_RS_ENABLE_PARITY_ENDPOINT", "0").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def create_debug_router() -> APIRouter:
    """Create debug router for migration/parity endpoints."""
    router = APIRouter(prefix="/api", tags=["Metadata"])

    @router.get("/debug/pipeline-parity")
    async def debug_pipeline_parity(
        repo_url: HttpUrl = Query(
            ...,
            description="URL of the code repository (GitHub, GitLab)",
        ),
        schema: str = Query(
            "maSMP",
            description="Schema to analyze against",
            enum=["maSMP", "CODEMETA"],
        ),
        access_token: Optional[str] = Query(
            None,
            description="Optional access token for private repositories",
        ),
        with_enrichment: bool = Query(
            False,
            description="Whether to compare enriched metadata parity as well",
        ),
    ):
        """
        Debug-only endpoint to compare legacy and pipeline extraction parity.

        Guarded by COMET_RS_ENABLE_PARITY_ENDPOINT and disabled by default.
        """
        if not _parity_endpoint_enabled():
            raise HTTPException(status_code=404, detail="Not found")

        try:
            parity = compare_legacy_and_pipeline_extraction(
                repo_url=str(repo_url),
                schema=schema,
                access_token=access_token,
                with_enrichment=with_enrichment,
            )
            return {"status": "success", "parity": parity}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return router
