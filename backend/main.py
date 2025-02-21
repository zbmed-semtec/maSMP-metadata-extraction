import copy
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from src.MetadataExtractor import process_repository
from src.constants import CombinedProperties
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic model for the response structure
class MetadataResponse(BaseModel):
    status: str
    schema: str
    code_url: HttpUrl
    message: str
    results: Dict[str, Any]

@app.get("/metadata", response_model=MetadataResponse)
async def extract_metadata(
    repo_url: HttpUrl = Query(..., description="URL of the code repository"),
    schema: str = Query(..., description="Schema to analyze against"),
    access_token: Optional[str] = Query(None, description="Optional access token for private repositories")
) -> MetadataResponse:
    """
    Extract metadata from a code repository using the provided schema.
    
    Args:
        repo_url: URL of the code repository to analyze
        schema: Schema to use for analysis
        access_token: Optional access token for private repositories
    
    Returns:
        MetadataResponse containing the analysis results
    """
    try:
        # Reset All_properties to None before each call
        All_properties = copy.deepcopy(CombinedProperties)

        # Process the repository using the same function as in Django version
        jsonld_document = process_repository(
            str(repo_url),
            All_properties,
            schema,
            access_token
        )

        # Return the response in the same format as the Django version
        return MetadataResponse(
            status="success",
            schema=schema,
            code_url=repo_url,
            message="Code analysis completed.",
            results=jsonld_document
        )

    except Exception as e:
        print(f"Error processing repository: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )