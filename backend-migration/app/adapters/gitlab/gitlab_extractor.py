"""
Layer 3: Adapters - GitLab
GitLab extractor - implements PlatformExtractor protocol
"""
from typing import Optional
from urllib.parse import quote
from datetime import datetime

from app.core.entities.repository_metadata import (
    RepositoryMetadata,
    VersionControlSystem,
    License,
)
from app.adapters.gitlab.gitlab_client import GitLabClient
from app.adapters.gitlab.gitlab_file_fetcher import GitLabFileFetcher
from app.domain.services.url_pattern_matcher import URLPatternMatcher


class GitLabExtractor:
    """
    GitLab platform extractor.
    Implements the PlatformExtractor protocol from Layer 2.
    """

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitLab extractor.

        Args:
            access_token (str | None): GitLab personal access token
        """
        self.client = GitLabClient(access_token)
        self.file_fetcher = GitLabFileFetcher(access_token)
        self.url_matcher = URLPatternMatcher()

    # -------------------------------------------------------------------------
    # Main extraction entry point
    # -------------------------------------------------------------------------
    def extract_platform_metadata(
        self, repo_url: str, access_token: Optional[str] = None
    ) -> RepositoryMetadata:
        """
        Extract metadata from GitLab via the GitLab API.

        Args:
            repo_url (str): GitLab repository URL.
            access_token (str | None): Optional access token override.

        Returns:
            RepositoryMetadata: Populated metadata object.
        """
        # Override tokens if provided at call time
        if access_token and not self.client.access_token:
            self.client = GitLabClient(access_token)
            self.file_fetcher = GitLabFileFetcher(access_token)

        # Extract project namespace + repo name (e.g., "remram44", "taguette")
        owner, repo = self.url_matcher.extract_repo_info(repo_url)
        if not owner or not repo:
            raise ValueError(f"Invalid GitLab repository URL: {repo_url}")

        # GitLab requires URL-encoded namespace/repo path:
        project_id = quote(f"{owner}/{repo}", safe="")

        # Retrieve core project metadata
        project = self.client.get_project(project_id)

        metadata = RepositoryMetadata()

        # ---------------------------------------------------------------------
        # Basic information
        # ---------------------------------------------------------------------
        metadata.name = project.get("name")
        metadata.description = project.get("description")
        metadata.url = project.get("web_url")
        metadata.codeRepository = project.get("http_url_to_repo")

        # ---------------------------------------------------------------------
        # Dates
        # ---------------------------------------------------------------------
        if project.get("created_at"):
            metadata.dateCreated = project["created_at"][:10]

        if project.get("last_activity_at"):
            metadata.dateModified = project["last_activity_at"][:10]

        # GitLab does not have "pushed_at", so we derive from last commit
        try:
            commits = self.client.get_commits(project_id, per_page=1)
            if commits:
                commit_date = commits[0]["committed_date"][:10]
                metadata.datePublished = commit_date
        except Exception:
            metadata.datePublished = None

        # ---------------------------------------------------------------------
        # Access control
        # ---------------------------------------------------------------------
        visibility = project.get("visibility", "").lower()
        metadata.conditionsOfAccess = visibility.capitalize()  # Public, Private, Internal
        metadata.isAccessibleForFree = str(visibility == "public")

        # ---------------------------------------------------------------------
        # Issue tracker and discussions
        # ---------------------------------------------------------------------
        metadata.issueTracker = project.get("web_url") + "/-/issues"
        metadata.codemeta_issueTracker = metadata.issueTracker

        if project.get("issues_enabled"):
            metadata.hasIssueTracker = True

        if project.get("operations_access_level") == "enabled":
            metadata.discussionUrl = project.get("web_url") + "/-/discussions"

        # ---------------------------------------------------------------------
        # Download archive
        # ---------------------------------------------------------------------
        metadata.downloadUrl = f"{project.get('web_url')}/-/archive/master/{project['name']}-master.zip"

        # ---------------------------------------------------------------------
        # Source code reference
        # ---------------------------------------------------------------------
        metadata.hasSourceCode = metadata.url
        metadata.codemeta_hasSourceCode = metadata.url

        # ---------------------------------------------------------------------
        # Keywords / Tags
        # ---------------------------------------------------------------------
        if project.get("tag_list"):
            metadata.keywords = project.get("tag_list")

        # ---------------------------------------------------------------------
        # Version control system
        # ---------------------------------------------------------------------
        metadata.masmp_versionControlSystem = VersionControlSystem.create_git(
            vcs_type="SoftwareSourceCode"
        )

        # ---------------------------------------------------------------------
        # Programming languages
        # ---------------------------------------------------------------------
        try:
            languages_data = self.client.get_languages(project_id)
            if languages_data:
                metadata.programmingLanguage = list(languages_data.keys())
        except Exception:
            pass

        # ---------------------------------------------------------------------
        # Contributors
        # ---------------------------------------------------------------------
        try:
            contributors = self.client.get_contributors(project_id)
            if contributors:
                metadata.contributor = [
                    {
                        "@type": "Person",
                        "name": c.get("name"),
                        "email": c.get("email"),
                    }
                    for c in contributors
                ]
        except Exception:
            pass

        # ---------------------------------------------------------------------
        # License
        # ---------------------------------------------------------------------
        try:
            license_data = self.client.get_license(project_id)
            if license_data and license_data.get("license"):
                l = license_data["license"]
                metadata.license = License(
                    name=l.get("name"),
                    url=l.get("url"),
                )
        except Exception:
            pass

        # ---------------------------------------------------------------------
        # README file
        # ---------------------------------------------------------------------
        for branch in ["main", "master"]:
            readme_url = f"https://gitlab.com/{owner}/{repo}/-/blob/{branch}/README.md"
            if self.file_fetcher.is_file_reachable(readme_url):
                metadata.codemeta_readme = readme_url
                break

        # ---------------------------------------------------------------------
        # CHANGELOG
        # ---------------------------------------------------------------------
        for branch in ["main", "master"]:
            changelog_url = f"https://gitlab.com/{owner}/{repo}/-/blob/{branch}/CHANGELOG.md"
            if self.file_fetcher.is_file_reachable(changelog_url):
                metadata.masmp_changelog = changelog_url
                break

        # ---------------------------------------------------------------------
        # Releases
        # ---------------------------------------------------------------------
        try:
            latest_release = self.client.get_latest_release(project_id)
            if latest_release:
                metadata.softwareVersion = latest_release.get("tag_name")
                metadata.version = latest_release.get("tag_name")
                metadata.has_release = True
            else:
                metadata.has_release = False
        except Exception:
            metadata.has_release = False

        return metadata
