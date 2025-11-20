"""
Layer 4: API / Frameworks
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.endpoints import metadata


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include routers
app.include_router(metadata.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Metadata Extractor API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

