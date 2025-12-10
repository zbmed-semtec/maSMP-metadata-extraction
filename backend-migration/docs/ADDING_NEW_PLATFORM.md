# Guide: Adding a New Platform

This guide shows you how to add support for a new platform (like GitLab, Codeberg, Bitbucket, etc.) to the metadata extraction system.

**Good News**: You only need to create a new adapter folder! Everything else stays the same.

---

## Overview

When you add a new platform, you need to:

1. Create a new adapter folder (e.g., `app/adapters/gitlab/`)
2. Implement the required functionality in that folder
3. Update existing files to recognize the new platform
4. That's it!

**Note**: You can organize your files however you want. You might create one file or many files - it's up to you. The important thing is that you implement the required functionality.

---

## Step-by-Step Guide

### Step 1: Create the Adapter Folder

Create a new folder for your platform:
**Example**: If you're adding GitLab, create `app/adapters/gitlab/`

---

### Step 2: Implement Your Platform Adapter

**Reference Implementation**: Look at `app/adapters/github/` to see how GitHub is implemented. Use it as a template for your platform.

The GitHub adapter contains:

- `github_client.py` - API client for GitHub
- `github_file_fetcher.py` - File downloader for GitHub
- `github_extractor.py` - Main extractor that implements the `PlatformExtractor` protocol

**What you need to do**:

1. Create similar files for your platform in your adapter folder
2. Adapt the code to work with your platform's API
3. Make sure your extractor class implements `extract_platform_metadata(repo_url, access_token) -> RepositoryMetadata`

**Important**:

- Different platforms have different APIs and capabilities
- You might need more or fewer files than GitHub
- You might need different methods depending on what your platform supports
- The key is to adapt the GitHub pattern to your platform's specific needs

Look at the files in `app/adapters/github/` to understand the pattern:

- `github_client.py` - See how it calls the GitHub API
- `github_file_fetcher.py` - See how it downloads files
- `github_extractor.py` - See how it implements `extract_platform_metadata()` and fills `RepositoryMetadata`

**Key things to note from GitHub implementation**:

- The extractor class must implement `extract_platform_metadata(repo_url, access_token) -> RepositoryMetadata`
- It uses the API client to fetch repository data
- It uses the file fetcher to download files (README, CITATION.cff, etc.)
- It maps platform-specific fields to `RepositoryMetadata` fields
- It returns a `RepositoryMetadata` object

**Adapt it to your platform**:

- Change API endpoints to match your platform
- Change authentication method if needed
- Adapt field mappings to your platform's API response
- Handle features your platform might not have (or skip them)
- Add features your platform has that GitHub doesn't

Remember: Different platforms have different capabilities. Don't worry if your platform doesn't support everything GitHub does - just implement what's available and map it to `RepositoryMetadata` fields.

---

### Step 3: Update Files to Recognize Your Platform

Now you need to update existing files so the system knows about your new platform.

#### Update `url_pattern_matcher.py`

Add your platform to the URL detection logic.

**File**: `app/domain/services/url_pattern_matcher.py`

**What to change**: Update the `detect_platform()` method:

```python
@staticmethod
def detect_platform(repo_url: str) -> Optional[str]:
    """
    Detect the platform from a repository URL.
  
    Args:
        repo_url: Repository URL
  
    Returns:
        Platform name (github, gitlab, etc.) or None
    """
    parsed_url = urlparse(repo_url)
    netloc = parsed_url.netloc.lower()
  
    if "github.com" in netloc:
        return "github"
  
    # Add your platform here
    if "gitlab.com" in netloc:
        return "gitlab"
  
    return None
```

**Also update** `extract_repo_info()` if your platform uses a different URL format:

```python
@staticmethod
def extract_repo_info(repo_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract owner and repository name from a repository URL.
  
    Args:
        repo_url: Repository URL
  
    Returns:
        tuple: (owner, repo_name) or (None, None) if extraction fails
    """
    parsed_url = urlparse(repo_url)
    parts = parsed_url.path.strip("/").split("/")
  
    # GitHub format: /owner/repo
    # GitLab format: /owner/repo (same)
    # Some platforms: /owner/group/repo (adjust if needed)
  
    if len(parts) < 2:
        return None, None
    return parts[-2], parts[-1]
```

---

#### Update `factory.py`

Add your platform to the factory that creates extractors.

**File**: `app/adapters/factory.py`

**What to change**: Import your extractor and add it to the factory:

```python
"""
Layer 3: Adapters - Factory
Factory pattern to select the correct platform extractor
"""
from typing import Optional
from app.adapters.github.github_extractor import GitHubExtractor
from app.adapters.gitlab.gitlab_extractor import GitLabExtractor  # Add this
from app.domain.services.url_pattern_matcher import URLPatternMatcher


class PlatformExtractorFactory:
    """Factory to create platform-specific extractors"""
  
    @staticmethod
    def create_extractor(repo_url: str, access_token: Optional[str] = None):
        """
        Create the appropriate platform extractor based on URL.
  
        Args:
            repo_url: Repository URL
            access_token: Optional access token
      
        Returns:
            Platform extractor instance
      
        Raises:
            ValueError: If platform is not supported
        """
        url_matcher = URLPatternMatcher()
        platform = url_matcher.detect_platform(repo_url)
  
        if platform == "github":
            return GitHubExtractor(access_token)
        elif platform == "gitlab":  # Add this
            return GitLabExtractor(access_token)
        else:
            raise ValueError(
                f"Unsupported platform: {platform}. "
                f"Supported platforms: GitHub, GitLab"  # Update this
            )
```

---

#### Update `file_parser_adapter.py`

Add your platform's file fetcher to the file parser adapter.

**File**: `app/adapters/file_parser_adapter.py`

**What to change**: Import your file fetcher and add it to the constructor:

```python
from app.adapters.github.github_file_fetcher import GitHubFileFetcher
from app.adapters.gitlab.gitlab_file_fetcher import GitLabFileFetcher  # Add this

class FileParserAdapter:
    def __init__(self, platform: str, access_token: Optional[str] = None, base_url: Optional[str] = None):
        # ... existing code ...
  
        if platform == "github":
            self.file_fetcher = GitHubFileFetcher(access_token)
        elif platform == "gitlab":  # Add this
            self.file_fetcher = GitLabFileFetcher(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
```

---

#### Update `external_data_fetcher_adapter.py`

Add your platform's file fetcher to the external data fetcher adapter.

**File**: `app/adapters/external_data_fetcher_adapter.py`

**What to change**: Same as Step 5 - import and add to constructor:

```python
from app.adapters.github.github_file_fetcher import GitHubFileFetcher
from app.adapters.gitlab.gitlab_file_fetcher import GitLabFileFetcher  # Add this

class ExternalDataFetcherAdapter:
    def __init__(self, platform: str, access_token: Optional[str] = None):
        # ... existing code ...
  
        if platform == "github":
            self.file_fetcher = GitHubFileFetcher(access_token)
        elif platform == "gitlab":  # Add this
            self.file_fetcher = GitLabFileFetcher(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
```

---

#### Update API Endpoint (Optional)

Update the endpoint description to mention your new platform.

**File**: `app/api/v1/endpoints/metadata.py`

**What to change**: Update the docstring and error messages:

```python
@router.get("/metadata", response_model=MetadataResponse)
async def extract_metadata(
    repo_url: HttpUrl = Query(
        ...,
        description="URL of the code repository (GitHub, GitLab)"  # Update this
    ),
    # ... rest of the code ...
):
    """
    Extract metadata from a code repository.
  
    This endpoint supports:
    - GitHub (github.com)
    - GitLab (gitlab.com)  # Add this
  
    # ... rest of the docstring ...
    """
    # ... in the code ...
    if not platform:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported repository platform. Supported: GitHub, GitLab"  # Update this
        )
```

---

### Step 4: Test Your Implementation

1. **Test URL detection**:

   ```python
   from app.domain.services.url_pattern_matcher import URLPatternMatcher
   matcher = URLPatternMatcher()
   print(matcher.detect_platform("https://gitlab.com/user/repo"))  # Should return "gitlab"
   ```
2. **Test factory**:

   ```python
   from app.adapters.factory import PlatformExtractorFactory
   extractor = PlatformExtractorFactory.create_extractor("https://gitlab.com/user/repo")
   print(type(extractor))  # Should be GitLabExtractor
   ```
3. **Test extraction**:

   ```python
   metadata = extractor.extract_platform_metadata("https://gitlab.com/user/repo")
   print(metadata.name)  # Should print the repo name
   ```
4. **Test the full flow**:

   ```bash
   # Run this command on the terminal to start the app
   uvicorn app.main:app --reload --port 8000 
   # **To run in termianl** (In another terminal use this command)
   curl "http://localhost:8000/api/v1/metadata?repo_url=https://gitlab.com/user/repo&schema=maSMP" # Use some real-time examples
   # **In browser**
   http://localhost:8000/docs#/

   ```

---

## Checklist

- [ ] Created adapter folder (`app/adapters/yourplatform/`)
- [ ] Created `__init__.py` file
- [ ] Reviewed GitHub implementation (`app/adapters/github/`) as reference
- [ ] Created files for your platform (adapt GitHub pattern to your platform's API)
- [ ] Implemented extractor class with `extract_platform_metadata()` method that returns `RepositoryMetadata`
- [ ] Updated `url_pattern_matcher.py` to detect your platform
- [ ] Updated `factory.py` to create your extractor
- [ ] Updated `file_parser_adapter.py` to use your file fetcher (if your platform supports file downloads)
- [ ] Updated `external_data_fetcher_adapter.py` to use your file fetcher (if your platform supports file downloads)
- [ ] Updated API endpoint documentation (optional)
- [ ] Tested URL detection
- [ ] Tested factory
- [ ] Tested extraction
- [ ] Tested full API flow

---

## Common Issues & Solutions

### Issue 1: "Unsupported platform" error

**Solution**: Make sure you updated `url_pattern_matcher.py` and `factory.py`

### Issue 2: File downloads fail

**Solution**: Check your platform's API format for file downloads. Some platforms use different endpoints.

### Issue 3: Authentication errors

**Solution**: Check your platform's authentication format (Bearer token, API key, etc.)

### Issue 4: Rate limiting

**Solution**: Make sure your `rate_limit_get()` method handles rate limits correctly (copy from GitHub example)

---

That's it! The rest of the code (use case, domain services, API) stays mostly the same.
