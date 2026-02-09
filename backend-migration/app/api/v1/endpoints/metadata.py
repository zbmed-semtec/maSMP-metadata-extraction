"""
Layer 4: API / Frameworks
FastAPI endpoints for metadata extraction
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from app.application.use_cases.extract_metadata import ExtractMetadataUseCase
from app.adapters.factory import PlatformExtractorFactory
from app.adapters.file_parser_adapter import FileParserAdapter
from app.adapters.external_data_fetcher_adapter import ExternalDataFetcherAdapter
from app.adapters.jsonld_builder import JSONLDBuilder
from app.domain.services.llm_extractor import LLMExtractor
from app.domain.services.url_pattern_matcher import URLPatternMatcher


router = APIRouter(prefix="/api/v1", tags=["Metadata"])


class MetadataResponse(BaseModel):
    """Response model for metadata extraction"""
    status: str
    schema: str
    code_url: HttpUrl
    message: str
    results: Dict[str, Any]

@router.get("/metadata", response_model=MetadataResponse)
async def extract_metadata(
    repo_url: HttpUrl = Query(
        ...,
        description="URL of the code repository (GitHub)"
    ),
    schema: str = Query(
        "maSMP",
        description="Schema to analyze against",
        enum=["maSMP", "CODEMETA"]
    ),
    access_token: Optional[str] = Query(None, description="Optional access token for private repositories")
) -> MetadataResponse:
    """
    Extract metadata from a code repository.
    
    This endpoint supports:
    - GitHub (github.com)
    
    Args:
        repo_url: URL of the repository
        schema: Schema to use (maSMP or CODEMETA)
        access_token: Optional access token for authentication
        
    Returns:
        MetadataResponse with extracted metadata
    """
    try:
        url_matcher = URLPatternMatcher()
        platform = url_matcher.detect_platform(str(repo_url))
        
        if not platform:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported repository platform. Supported: GitHub"
            )
        
        # Create platform-specific adapters
        platform_extractor = PlatformExtractorFactory.create_extractor(str(repo_url), access_token)
        file_parser = FileParserAdapter(platform, access_token)
        external_data_fetcher = ExternalDataFetcherAdapter(platform, access_token)
        
        # Create use case with all dependencies
        llm_extractor = LLMExtractor()  # TODO: Add API key from config
        jsonld_builder = JSONLDBuilder()
        
        use_case = ExtractMetadataUseCase(
            platform_extractor=platform_extractor,
            file_parser=file_parser,
            external_data_fetcher=external_data_fetcher,
            llm_extractor=llm_extractor,
            jsonld_builder=jsonld_builder
        )
        
        # Execute use case
        jsonld_document = use_case.execute(
            repo_url=str(repo_url),
            schema=schema,
            access_token=access_token
        )
        
        return MetadataResponse(
            status="success",
            schema=schema,
            code_url=repo_url,
            message="Code analysis completed.",
            results=jsonld_document
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "service": "metadata-extractor"}


@router.get("/platforms")
async def get_supported_platforms():
    """
    Get list of supported platforms.
    
    Returns:
        List of supported platforms
    """
    return {
        "platforms": [
            {
                "name": "GitHub",
                "url_pattern": "github.com",
                "description": "GitHub repositories"
            }
        ]
    }

