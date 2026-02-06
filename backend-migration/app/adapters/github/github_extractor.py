"""
Layer 3: Adapters - GitHub
GitHub extractor - implements PlatformExtractor protocol
"""
from typing import Optional
from datetime import datetime
from app.core.entities.repository_metadata import RepositoryMetadata, VersionControlSystem, License
from app.adapters.github.github_client import GitHubClient
from app.adapters.github.github_file_fetcher import GitHubFileFetcher
from app.domain.services.url_pattern_matcher import URLPatternMatcher


class GitHubExtractor:
    """
    GitHub platform extractor.
    Implements the PlatformExtractor protocol from Layer 2.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitHub extractor.
        
        Args:
            access_token: GitHub access token
        """
        self.client = GitHubClient(access_token)
        self.file_fetcher = GitHubFileFetcher(access_token)
        self.url_matcher = URLPatternMatcher()
    
    def extract_platform_metadata(self, repo_url: str, access_token: Optional[str] = None) -> RepositoryMetadata:
        """
        Extract metadata from GitHub API.
        
        Args:
            repo_url: GitHub repository URL
            access_token: Access token (if not set in constructor)
            
        Returns:
            RepositoryMetadata object
        """
        if access_token and not self.client.access_token:
            self.client = GitHubClient(access_token)
            self.file_fetcher = GitHubFileFetcher(access_token)
        
        owner, repo = self.url_matcher.extract_repo_info(repo_url)
        if not owner or not repo:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        
        # Fetch repository data
        repo_data = self.client.get_repo(owner, repo)
        
        # Create metadata object
        metadata = RepositoryMetadata()
        
        # Basic information
        metadata.name = repo_data.get("name")
        metadata.description = repo_data.get("description")
        metadata.url = repo_data.get("html_url")
        metadata.codeRepository = f"{repo_data.get('html_url')}.git"
        
        # Dates
        if repo_data.get("created_at"):
            metadata.dateCreated = repo_data.get("created_at")[:10]
        if repo_data.get("updated_at"):
            metadata.dateModified = repo_data.get("updated_at")[:10]
        if repo_data.get("pushed_at"):
            metadata.datePublished = repo_data.get("pushed_at")[:10]
        
        # Access information
        is_private = repo_data.get("private", False)
        metadata.conditionsOfAccess = "Private" if is_private else "Public"
        metadata.isAccessibleForFree = str(not is_private)
        
        # Issue tracker and discussion
        metadata.issueTracker = f"{repo_data.get('html_url')}/issues"
        metadata.codemeta_issueTracker = metadata.issueTracker
        if repo_data.get("has_discussions"):
            metadata.discussionUrl = f"{repo_data.get('html_url')}/discussions"
        
        # Download URL
        archive_url = repo_data.get("archive_url", "")
        if archive_url:
            metadata.downloadUrl = archive_url.replace("{archive_format}{/ref}", "zipball/master")
        
        # Source code
        metadata.hasSourceCode = f"{repo_data.get('html_url')}#id"
        metadata.codemeta_hasSourceCode = metadata.hasSourceCode
        
        # Keywords (topics)
        if repo_data.get("topics"):
            metadata.keywords = repo_data.get("topics")
        
        # Version control system (default to SoftwareSourceCode, can be changed based on profile)
        metadata.masmp_versionControlSystem = VersionControlSystem.create_git(
            vcs_type="SoftwareSourceCode"
        )
        
        # Programming languages
        try:
            languages_data = self.client.get_languages(owner, repo)
            if languages_data:
                metadata.programmingLanguage = list(languages_data.keys())
        except Exception:
            pass
        
        # Contributors
        try:
            contributors_data = self.client.get_contributors(owner, repo)
            if contributors_data:
                metadata.contributor = [
                    {"@type": "Person", "url": c.get("html_url")}
                    for c in contributors_data
                ]
        except Exception:
            pass
        
        # License
        try:
            license_data = self.client.get_license(owner, repo)
            if license_data and license_data.get("license"):
                license_info = license_data["license"]
                metadata.license = License(
                    name=license_info.get("name"),
                    url=license_info.get("url")
                )
        except Exception:
            pass
        
        # README
        for branch in ["main", "master"]:
            readme_url = f"https://github.com/{owner}/{repo}/blob/{branch}/README.md"
            if self.file_fetcher.is_file_reachable(readme_url):
                metadata.codemeta_readme = readme_url
                break
        
        # CHANGELOG
        for branch in ["main", "master"]:
            changelog_url = f"https://github.com/{owner}/{repo}/blob/{branch}/CHANGELOG.md"
            if self.file_fetcher.is_file_reachable(changelog_url):
                metadata.masmp_changelog = changelog_url
                break
        
        # Release information
        try:
            release_data = self.client.get_latest_release(owner, repo)
            if release_data:
                metadata.softwareVersion = release_data.get("tag_name")
                if release_data.get("published_at"):
                    release_date = release_data.get("published_at")[:10]
                    # Check if latest commit is before or same as release
                    try:
                        commits_data = self.client.get_commits(owner, repo, per_page=1)
                        if commits_data:
                            commit_date = commits_data[0]["commit"]["committer"]["date"][:10]
                            if commit_date <= release_date:
                                metadata.version = release_data.get("tag_name")
                    except Exception:
                        pass
                
                # Store has_release flag (we'll use this in the use case)
                metadata.has_release = True
        except Exception:
            metadata.has_release = False
        
        return metadata

