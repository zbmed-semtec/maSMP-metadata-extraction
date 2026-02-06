# Developer Guide

Welcome! This guide explains how the metadata extraction system works. Even if you're new to Python or clean architecture, this guide will help you understand the codebase.

## Table of Contents
1. [What This Project Does](#what-this-project-does)
2. [Architecture Overview](#architecture-overview)
3. [The 4 Layers Explained](#the-4-layers-explained)
4. [How Data Flows](#how-data-flows)
5. [Key Concepts](#key-concepts)
6. [File Structure](#file-structure)

---

## What This Project Does

**Goal**: Take any public repository URL (like `https://github.com/user/repo`) and extract rich metadata (fields: name, description, license, authors, programming languages, etc.).

**Output**: A JSON-LD document with all the metadata, ready to use.

**Example**: 
- **Input**: `https://github.com/octocat/Hello-World`
- **Output**: JSON with name, description, license, authors, languages, etc.

---

## Architecture Overview

We use **Clean Architecture** (also called "Onion Architecture"). Think of it like an onion with 4 layers:

```
┌─────────────────────────────────────┐
│  Layer 4: Frameworks (FastAPI)      │  ← Outside (Web API)
├─────────────────────────────────────┤
│  Layer 3: Adapters & Services       │  ← Workers (GitHub API, Parsers)
├─────────────────────────────────────┤
│  Layer 2: Use Cases                 │  ← Chief (Orchestration)
├─────────────────────────────────────┤
│  Layer 1: Entities (Data Models)    │  ← Core (Data Structure)
└─────────────────────────────────────┘
```

**The Golden Rule**: Code can only import from layers **inside** it, never from layers **outside** it.

- Layer 4 can import from Layers 3, 2, 1
- Layer 3 can import from Layers 2, 1
- Layer 2 can import from Layer 1 only
- Layer 1 imports nothing (pure data models)

This keeps the code organized and makes it easy to add new platforms without breaking existing code.

---

## The 4 Layers Explained

### Layer 1: Core / Entities (The Data Model)

**Location**: `app/core/entities/repository_metadata.py`

**What it is**: The central data structure. This is what we're trying to fill with metadata.

**Key File**: `repository_metadata.py` contains:
- `RepositoryMetadata` - The main model with 30+ fields
- `Person` - For authors, contributors, maintainers
- `VersionControlSystem` - For Git, SVN, etc.
- `License` - For license information
- `ReferencePublication` - For research papers/citations

**Example**:
```python
metadata = RepositoryMetadata()
metadata.name = "My Project"
metadata.description = "A cool project"
metadata.license = License(name="MIT", url="https://...")
```

**Why it's important**: This is the **only** data model. No matter which platform (GitHub, GitLab, etc.), we always fill the same `RepositoryMetadata` object.

---

### Layer 2: Application / Use Cases (The chief)

**Location**: `app/application/use_cases/extract_metadata.py`

**What it is**: The "chief" that coordinates everything. It doesn't do the actual work, it just tells others what to do.

**Key File**: `extract_metadata.py` contains:
- `ExtractMetadataUseCase` - The main orchestrator
- Protocol definitions (interfaces) - What tools the chief needs

**The 5 Fixed Steps** (always in this order):
1. **Extract platform metadata** - Get data from GitHub API
2. **Parse repository files** - Read README, CITATION.cff, LICENSE
3. **Fetch external data** - Get data from OpenAlex, Wayback Machine
4. **Extract with LLM** - Use AI to find more metadata (optional)
5. **Build JSON-LD** - Convert to final output format

**Example**:
```python
use_case = ExtractMetadataUseCase(
    platform_extractor=github_extractor,  # Tool 1
    file_parser=file_parser,              # Tool 2
    external_data_fetcher=fetcher,        # Tool 3
    llm_extractor=llm_extractor,          # Tool 4
    jsonld_builder=builder                # Tool 5
)

result = use_case.execute(repo_url="https://github.com/...")
```

**Why it's important**: This is the **only** place that defines the 5-step process. If you want to change the order or add a step, you do it here.

**Dependency Injection**: The use case doesn't create tools. FastAPI (Layer 4) creates the tools and gives them to the use case. This is called "dependency injection."

---

### Layer 3: Domain Services + Adapters (The Workers)

**Location**: 
- `app/domain/services/` - Shared workers (not platform-specific)
- `app/adapters/` - Platform-specific workers

**What it is**: The actual workers that do the real work.

#### Domain Services (Shared Workers)

These work for **any** platform:

- `url_pattern_matcher.py` - Detects which platform from URL
- `citation_file_parser.py` - Parses CITATION.cff files
- `readme_parser.py` - Parses README.md files
- `openalex_client.py` - Fetches publication data from OpenAlex
- `wayback_client.py` - Checks if URLs are archived
- `llm_extractor.py` - Uses AI to extract metadata

#### Adapters (Platform-Specific Workers)

These are **platform-specific**:

**GitHub Adapter** (`app/adapters/github/`):
- `github_client.py` - Talks to GitHub API
- `github_file_fetcher.py` - Downloads files from GitHub
- `github_extractor.py` - Extracts metadata from GitHub API

**Generic Adapters** (`app/adapters/`):
- `factory.py` - Creates the right platform extractor (GitHub, GitLab, etc.)
- `file_parser_adapter.py` - Uses platform file fetcher + domain parsers
- `external_data_fetcher_adapter.py` - Uses platform file fetcher + external APIs
- `jsonld_builder.py` - Converts RepositoryMetadata to JSON-LD

**Example**:
```python
# GitHub-specific
github_client = GitHubClient(access_token="...")
repo_data = github_client.get_repo("owner", "repo")

# Shared service (works for any platform)
citation_parser = CitationFileParser()
metadata = citation_parser.parse_citation_cff(content, metadata)
```

**Why it's important**: When you add a new platform (like GitLab), you only add a new adapter folder. Everything else stays the same!

---

### Layer 4: Frameworks (The API)

**Location**: `app/api/v1/endpoints/metadata.py`

**What it is**: The FastAPI endpoint that receives HTTP requests and returns responses.

**Key File**: `metadata.py` contains:
- `extract_metadata()` - The main endpoint
- `create_use_case()` - Creates all tools and gives them to the use case

**Example Request**:
```bash
GET /api/v1/metadata?repo_url=https://github.com/octocat/Hello-World&schema=maSMP
```

**What happens**:
1. FastAPI receives the request
2. FastAPI creates all the tools (GitHub client, parsers, etc.)
3. FastAPI creates the use case and gives it the tools
4. FastAPI calls `use_case.execute()`
5. FastAPI returns the JSON-LD result

**Example**:
```python
@router.get("/metadata")
async def extract_metadata(repo_url: str, schema: str):
    # Create tools
    platform_extractor = PlatformExtractorFactory.create_extractor(repo_url)
    file_parser = FileParserAdapter("github")
    # ... create other tools
    
    # Create use case with tools
    use_case = ExtractMetadataUseCase(
        platform_extractor=platform_extractor,
        file_parser=file_parser,
        # ... other tools
    )
    
    # Execute
    result = use_case.execute(repo_url, schema)
    return result
```

**Why it's important**: This is the **only** place that knows about FastAPI. If you want to change to Flask or Django, you only change this layer.

---

## How Data Flows

Here's what happens when you call the API:

```
1. User sends request
   ↓
2. FastAPI endpoint receives it
   ↓
3. FastAPI creates all tools (GitHub client, parsers, etc.)
   ↓
4. FastAPI creates use case and gives it the tools
   ↓
5. Use case executes 5 steps:
   ├─ Step 1: GitHub extractor gets data → fills RepositoryMetadata
   ├─ Step 2: File parser reads README/CITATION → updates RepositoryMetadata
   ├─ Step 3: External fetcher gets OpenAlex data → updates RepositoryMetadata
   ├─ Step 4: LLM extractor finds more data → updates RepositoryMetadata
   └─ Step 5: JSON-LD builder converts RepositoryMetadata → JSON-LD
   ↓
6. Use case returns JSON-LD
   ↓
7. FastAPI returns JSON-LD to user
```

**Key Point**: The `RepositoryMetadata` object flows through all 5 steps, getting filled with more and more data at each step.

---

## Key Concepts

### 1. Dependency Injection

**What it is**: Instead of creating tools inside the use case, we give the tools to the use case from outside.

**Why**: This makes the code testable and flexible. You can swap GitHub for GitLab without changing the use case.

**Example**:
```python
# ❌ Bad: Use case creates its own tools
class UseCase:
    def execute(self, repo_url):
        github = GitHubClient()  # Hard-coded!
        # ...

# ✅ Good: Tools are injected
class UseCase:
    def __init__(self, platform_extractor):
        self.platform_extractor = platform_extractor  # Given from outside!
    
    def execute(self, repo_url):
        self.platform_extractor.extract(...)  # Works with any platform!
```

### 2. Protocols (Interfaces)

**What it is**: A "contract" that says "any tool that implements this protocol can be used here."

**Why**: The use case doesn't care if it's GitHub or GitLab, as long as it follows the protocol.

**Example**:
```python
# Protocol definition (what the use case needs)
class PlatformExtractor(Protocol):
    def extract_platform_metadata(self, repo_url: str) -> RepositoryMetadata:
        ...

# GitHub implementation
class GitHubExtractor:
    def extract_platform_metadata(self, repo_url: str) -> RepositoryMetadata:
        # GitHub-specific code
        ...

# Use case accepts any PlatformExtractor
use_case = ExtractMetadataUseCase(platform_extractor=GitHubExtractor())
```

### 3. Factory Pattern

**What it is**: A function that creates the right tool based on input.

**Why**: We don't want the use case to know about GitHub vs GitLab. The factory decides.

**Example**:
```python
# Factory decides which extractor to create
extractor = PlatformExtractorFactory.create_extractor(repo_url)
# Returns GitHubExtractor if URL is GitHub
# Returns GitLabExtractor if URL is GitLab
```

---

## File Structure

```
app/
├── core/
│   └── entities/
│       └── repository_metadata.py    # Layer 1: Data model
│
├── application/
│   └── use_cases/
│       └── extract_metadata.py        # Layer 2: Orchestration
│
├── domain/
│   └── services/                      # Layer 3: Shared workers
│       ├── citation_file_parser.py
│       ├── readme_parser.py
│       ├── url_pattern_matcher.py
│       ├── openalex_client.py
│       ├── wayback_client.py
│       └── llm_extractor.py
│
├── adapters/                          # Layer 3: Platform workers
│   ├── github/
│   │   ├── github_client.py
│   │   ├── github_file_fetcher.py
│   │   └── github_extractor.py
│   ├── factory.py                     # Creates platform extractors
│   ├── file_parser_adapter.py         # Uses platform file fetcher
│   ├── external_data_fetcher_adapter.py # Uses platform file fetcher
│   └── jsonld_builder.py              # Converts to JSON-LD
│
└── api/
    └── v1/
        └── endpoints/
            └── metadata.py            # Layer 4: FastAPI endpoint
```

---

## Summary

1. **Layer 1 (Entities)**: The data model (`RepositoryMetadata`)
2. **Layer 2 (Use Cases)**: The chief that orchestrates 5 steps
3. **Layer 3 (Services + Adapters)**: The workers that do the actual work
4. **Layer 4 (API)**: The FastAPI endpoint

**The Flow**:
- Request → FastAPI → Use Case → Tools → RepositoryMetadata → JSON-LD → Response

---

## Next Steps

- Read [ADDING_NEW_PLATFORM.md](./ADDING_NEW_PLATFORM.md) to learn how to add a new platform
- Check the code comments for more details
- Run the tests to see how everything works together

