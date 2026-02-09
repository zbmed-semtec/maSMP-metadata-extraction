"""
Layer 4: API / Frameworks – Routes only.
Schemas in api/schemas; composition in api/services.
"""
import asyncio
import json
import queue
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import HttpUrl

from app.domain.services.url_pattern_matcher import URLPatternMatcher
from app.api.services.metadata_service import run_extraction, run_extraction_with_progress
from app.api.schemas.metadata import MetadataPlainResponse, MetadataEnrichedResponse
from app.application.use_cases.extract_metadata import EXTRACTION_STEPS

# Step ID -> human-readable label for SSE progress events
STEP_LABELS = {step_id: label for step_id, label in EXTRACTION_STEPS}


router = APIRouter(prefix="/api", tags=["Metadata"])


@router.get("/metadata", response_model=MetadataPlainResponse)
async def extract_metadata_plain(
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
) -> MetadataPlainResponse:
    """
    Extract metadata and return **only** the maSMP/CODEMETA JSON-LD.

    Use this for: download, scripts, interoperability. No confidence/source/category.
    For UI enrichment (confidence, source, category per property), use GET /metadata/enriched.
    """
    try:
        url_matcher = URLPatternMatcher()
        platform = url_matcher.detect_platform(str(repo_url))
        if not platform:
            raise HTTPException(
                status_code=400,
                detail="Unsupported repository platform. Supported: GitHub, GitLab",
            )

        jsonld_document, _ = run_extraction(
            repo_url=str(repo_url),
            schema=schema,
            access_token=access_token,
            with_enrichment=False,
        )

        return MetadataPlainResponse(
            status="success",
            schema_=schema,
            code_url=repo_url,
            message="Code analysis completed.",
            results=jsonld_document,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/metadata/enriched", response_model=MetadataEnrichedResponse)
async def extract_metadata_enriched(
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
) -> MetadataEnrichedResponse:
    """
    Extract metadata and return JSON-LD **plus** per-property enrichment.

    Returns results (maSMP/CODEMETA JSON-LD) and enriched_metadata (confidence, source, category per property).
    Use this for: UI display. For download or schema-only consumers, use GET /metadata.
    """
    try:
        url_matcher = URLPatternMatcher()
        platform = url_matcher.detect_platform(str(repo_url))
        if not platform:
            raise HTTPException(
                status_code=400,
                detail="Unsupported repository platform. Supported: GitHub, GitLab",
            )

        jsonld_document, enriched = run_extraction(
            repo_url=str(repo_url),
            schema=schema,
            access_token=access_token,
            with_enrichment=True,
        )

        if not enriched:
            enriched = {}

        return MetadataEnrichedResponse(
            status="success",
            schema_=schema,
            code_url=repo_url,
            message="Code analysis completed.",
            results=jsonld_document,
            enriched_metadata=enriched,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _format_sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_metadata_events(
    repo_url: str,
    schema: str,
    access_token: Optional[str],
):
    """Async generator that yields SSE events: progress for each step, then enriched result or error."""
    progress_queue = queue.Queue()

    def progress_callback(step_id: str, status: str) -> None:
        progress_queue.put({
            "event": "progress",
            "step": step_id,
            "status": status,
            "label": STEP_LABELS.get(step_id, step_id),
        })

    result_holder = []

    def run_extraction_sync() -> None:
        try:
            jsonld_document, enriched = run_extraction_with_progress(
                repo_url=repo_url,
                schema=schema,
                access_token=access_token,
                with_enrichment=True,
                progress_callback=progress_callback,
            )
            result_holder.append(("ok", jsonld_document, enriched))
        except Exception as e:
            result_holder.append(("error", str(e), None))

    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, run_extraction_sync)

    while not future.done() or not progress_queue.empty():
        try:
            item = progress_queue.get_nowait()
            yield _format_sse("progress", item)
        except queue.Empty:
            if future.done():
                break
            await asyncio.sleep(0.05)

    await future
    if not result_holder:
        yield _format_sse("error", {"detail": "Extraction produced no result."})
        return
    status, first, second = result_holder[0]
    if status == "error":
        yield _format_sse("error", {"detail": first})
        return
    jsonld_document, enriched = first, second
    payload = {
        "status": "success",
        "schema": schema,
        "code_url": repo_url,
        "message": "Code analysis completed.",
        "results": jsonld_document,
        "enriched_metadata": enriched or {},
    }
    yield _format_sse("result", payload)


@router.get("/metadata/stream")
async def extract_metadata_stream(
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
):
    """
    Extract metadata with live progress, then return enriched result (SSE).

    Same data as GET /metadata/enriched, but streams progress events first.
    Events:
    - **progress**: `{ "step", "status", "label" }` — step is one of platform, file_parsing,
      external_data, llm, jsonld_build; status is "started" or "completed".
    - **result**: full enriched response (same shape as GET /metadata/enriched).
    - **error**: `{ "detail": "..." }` if extraction failed.
    """
    try:
        url_matcher = URLPatternMatcher()
        platform = url_matcher.detect_platform(str(repo_url))
        if not platform:
            raise HTTPException(
                status_code=400,
                detail="Unsupported repository platform. Supported: GitHub, GitLab",
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        _stream_metadata_events(
            repo_url=str(repo_url),
            schema=schema,
            access_token=access_token,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
