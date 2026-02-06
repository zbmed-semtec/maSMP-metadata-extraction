# Backend Migration - Clean Architecture

This is the migrated backend using clean architecture principles.

## Architecture Overview

The application follows a 4-layer clean architecture (onion architecture):

### Layer 1: Core / Entities (Center)
- **Location**: `app/core/entities/`
- **Contains**: `RepositoryMetadata` - The final data model with 30+ fields
- **Rule**: No dependencies on other layers

### Layer 2: Application / Use Cases
- **Location**: `app/application/use_cases/`
- **Contains**: `ExtractMetadataUseCase` - The orchestration layer
- **Rule**: Only imports from Layer 1. Uses dependency injection for tools.

### Layer 3: Domain Services + Adapters
- **Location**: `app/domain/services/` and `app/adapters/`
- **Contains**: 
  - Domain Services: Shared tools (LLM, OpenAlex, Wayback, parsers)
  - Adapters: Platform-specific clients (GitHub)
- **Rule**: Can import from Layer 2

### Layer 4: Frameworks / API
- **Location**: `app/api/` and `app/main.py`
- **Contains**: FastAPI routes and application setup
- **Rule**: Can import from Layer 3 and Layer 2

## Installation

```bash
conda create -n metadata-extractor
conda activate metadata-extractor
```

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

To test the migration:

1. Start the server
2. Test in swagger: http://localhost:8000/docs and try out the APIs
2. Test in Terminal:
   ```bash
   curl "http://localhost:8000/api/v1/metadata?repo_url={URL}"
   ```

## Documentation

- **[DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)** - Complete guide explaining the codebase, architecture, and how everything works. Perfect for new developers!
- **[ADDING_NEW_PLATFORM.md](./docs/ADDING_NEW_PLATFORM.md)** - Step-by-step guide for adding support for new platforms (GitLab, Codeberg, etc.)


