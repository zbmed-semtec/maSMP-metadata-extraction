"""
Layer 3: Adapters - Codeberg
Codeberg extractor - implements PlatformExtractor protocol
"""
from typing import Optional, TYPE_CHECKING
from core.entities.repository_metadata import RepositoryMetadata, VersionControlSystem, License
from adapters.codeberg.codeberg_client import CodebergClient
from adapters.codeberg.codeberg_file_fetcher import CodebergFileFetcher
from domain.services.url_pattern_matcher import URLPatternMatcher
from domain.extraction_sources import SOURCE_CODEBERG_API, CONFIDENCE_PLATFORM, SOURCE_LICENSE_FILE, CONFIDENCE_LICENSE

if TYPE_CHECKING:
    from application.use_cases.extract_metadata import ExtractionMetadataCollector


class CodebergExtractor:
    """
    Codeberg platform extractor.
    Implements the PlatformExtractor protocol from Layer 2.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Codeberg extractor.
        
        Args:
            access_token: Codeberg access token
        """
        self.client = CodebergClient(access_token)
        self.file_fetcher = CodebergFileFetcher(access_token)
        self.url_matcher = URLPatternMatcher()
    
    def extract_platform_metadata(
        self,
        repo_url: str,
        access_token: Optional[str] = None,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> RepositoryMetadata:
        """
        Extract metadata from Codeberg API.

        Args:
            repo_url: Codeberg repository URL
            access_token: Access token (if not set in constructor)
            extraction_metadata: Optional collector for source/confidence per property

        Returns:
            RepositoryMetadata object
        """
        def record(field: str) -> None:
            if extraction_metadata is not None:
                extraction_metadata.record(field, SOURCE_CODEBERG_API, CONFIDENCE_PLATFORM)

        # import time
        # _start = time.time()
        # def _elapsed():
        #     return f"{time.time() - _start:.3f}s"

        # print(f"[DEBUG][{_elapsed()}] Starting Codeberg extraction for: {repo_url}")

        if access_token and not self.client.access_token:
            self.client = CodebergClient(access_token)
            self.file_fetcher = CodebergFileFetcher(access_token)

        # print(f"[DEBUG][{_elapsed()}] Extracting owner/repo from URL")
        owner, repo = self.url_matcher.extract_repo_info(repo_url)
        if not owner or not repo:
            raise ValueError(f"Invalid Codeberg repository URL: {repo_url}")

        # print(f"[DEBUG][{_elapsed()}] Fetching repo data for {owner}/{repo}")
        repo_data = self.client.get_repo(owner, repo)
        # print(f"[DEBUG][{_elapsed()}] Repo data fetched")
        metadata = RepositoryMetadata()

        # Basic information
        metadata.name = repo_data.get("name")
        metadata.description = repo_data.get("description")
        metadata.url = repo_data.get("html_url")
        metadata.codeRepository = f"{repo_data.get('html_url')}.git"
        if metadata.name is not None:
            record("name")
        if metadata.description is not None:
            record("description")
        if metadata.url is not None:
            record("url")
        if metadata.codeRepository is not None:
            record("codeRepository")

        # Dates
        if repo_data.get("created_at"):
            metadata.dateCreated = repo_data.get("created_at")[:10]
            record("dateCreated")
        if repo_data.get("updated_at"):
            metadata.dateModified = repo_data.get("updated_at")[:10]
            record("dateModified")
        if repo_data.get("pushed_at"):
            metadata.datePublished = repo_data.get("pushed_at")[:10]
            record("datePublished")

        # Access information
        is_private = repo_data.get("private", False)
        metadata.conditionsOfAccess = "Private" if is_private else "Public"
        metadata.isAccessibleForFree = str(not is_private)
        record("conditionsOfAccess")
        record("isAccessibleForFree")

        # Issue tracker and discussion
        metadata.issueTracker = f"{repo_data.get('html_url')}/issues"
        metadata.codemeta_issueTracker = metadata.issueTracker
        record("issueTracker")
        record("codemeta_issueTracker")
        if repo_data.get("has_discussions"):
            metadata.discussionUrl = f"{repo_data.get('html_url')}/discussions"
            record("discussionUrl")

        # Download URL
        archive_url = repo_data.get("archive_url", "")
        if archive_url:
            metadata.downloadUrl = archive_url.replace("{archive_format}{/ref}", "zipball/master")
            record("downloadUrl")

        # Source code
        metadata.hasSourceCode = f"{repo_data.get('html_url')}#id"
        metadata.codemeta_hasSourceCode = metadata.hasSourceCode
        record("hasSourceCode")
        record("codemeta_hasSourceCode")

        # Keywords (topics) — merge with any existing from other sources
        topics = repo_data.get("topics") or []
        if topics:
            existing = metadata.keywords or []
            metadata.keywords = list(set(existing) | set(topics))
            record("keywords")

        # Version control system
        metadata.masmp_versionControlSystem = VersionControlSystem.create_git(
            vcs_type="SoftwareSourceCode"
        )
        record("masmp_versionControlSystem")

        # Programming languages
        # print(f"[DEBUG][{_elapsed()}] Fetching programming languages")
        try:
            languages_data = self.client.get_languages(owner, repo)
            # print(f"[DEBUG][{_elapsed()}] Languages fetched: {list(languages_data.keys()) if languages_data else 'none'}")
            if languages_data:
                metadata.programmingLanguage = list(languages_data.keys())
                record("programmingLanguage")
        except Exception as e:
            # print(f"[DEBUG][{_elapsed()}] Languages fetch failed: {e}")
            pass

        # Contributors
        # print(f"[DEBUG][{_elapsed()}] Fetching contributors")
        try:
            #import pdb; pdb.set_trace()
            contributors_data = self.client.get_contributors(owner, repo)
            # print(f"[DEBUG][{_elapsed()}] Contributors fetched: {len(contributors_data) if contributors_data else 0} contributors")
            if contributors_data:
                metadata.contributor = [
                    {"@type": "Person", "url": c.get("html_url")}
                    for c in contributors_data
                ]
                record("contributor")
        except Exception as e:
            # print(f"[DEBUG][{_elapsed()}] Contributors fetch failed: {e}")
            pass

        # print(f"[DEBUG][{_elapsed()}] Listing repo contents")
        repo_contents = self.file_fetcher.list_repo_contents(owner, repo)
        # print(f"[DEBUG][{_elapsed()}] Repo contents listed: {len(repo_contents) if repo_contents else 0} items")

        # License
        # print(f"[DEBUG][{_elapsed()}] Scanning for LICENSE file")
        license_candidates = [
            file for file in repo_contents 
                if 'LICENSE' in file.get('name', '') 
                and file.get('type', '') == 'file']
        # print(f"[DEBUG][{_elapsed()}] LICENSE candidates found: {[f.get('name') for f in license_candidates]}")
        if len(license_candidates) == 1:
            license_file = license_candidates[0]
            # print(f"[DEBUG][{_elapsed()}] Fetching LICENSE content from: {license_file.get('download_url')}")
            license_content = self.file_fetcher.fetch_file_content(license_file.get('download_url'))
            # print(f"[DEBUG][{_elapsed()}] LICENSE content fetched ({len(license_content) if license_content else 0} chars)")
            license_url = license_file.get('html_url')
            license_name = license_content.split('\n')[0].strip()
            license_meta = License(name=license_name, url=license_url)
            metadata.license = license_meta
            if extraction_metadata:
                extraction_metadata.record('license', SOURCE_LICENSE_FILE, CONFIDENCE_LICENSE)

        # README
        # print(f"[DEBUG][{_elapsed()}] Scanning for README file")
        readme_candidates = [
            file for file in repo_contents 
                if 'README' in file.get('name', '') 
                and file.get('type', '') == 'file']
        # print(f"[DEBUG][{_elapsed()}] README candidates found: {[f.get('name') for f in readme_candidates]}")
        if len(readme_candidates) == 1:
            readme = readme_candidates[0]
            metadata.codemeta_readme = readme.get('html_url')
            record('codemeta_readme')

        # CHANGELOG
        # print(f"[DEBUG][{_elapsed()}] Scanning for CHANGELOG file")
        changelog_candidates = [
            file for file in repo_contents 
                if 'CHANGELOG' in file.get('name', '') 
                and file.get('type', '') == 'file']
        # print(f"[DEBUG][{_elapsed()}] CHANGELOG candidates found: {[f.get('name') for f in changelog_candidates]}")
        if len(changelog_candidates) == 1:
            changelog = changelog_candidates[0]
            metadata.masmp_changelog = changelog.get('html_url')
            record('masmp_changelog')

        # Software requirements files (root-level and nested)
        # print(f"[DEBUG][{_elapsed()}] Starting requirements file scan")
        requirement_files = {
            "requirements.txt",
            "environment.yml",
            "environment.yaml",
            "Pipfile",
            "pyproject.toml",
            "setup.cfg",
            "setup.py",
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
        }
        requirement_urls: list[str] = []

        # requirements
        requirement_candidates = [
            file 
                for file in repo_contents 
                if file.get('name') in requirement_files
                or file.get('name', '').endswith('.lock')
                and file.get('type') == 'file'
        ]
        # print(f"[DEBUG][{_elapsed()}] requirement candidates found: {[f.get('name') for f in requirement_candidates]}")
        requirement_urls = [requirement.get('html_url') for requirement in requirement_candidates if requirement.get('html_url') is not None]
        
        # print(f"[DEBUG][{_elapsed()}] requirement urls are: {requirement_urls}")
        if len(requirement_urls) > 0:
            metadata.softwareRequirements = requirement_urls
            record("softwareRequirements")
        
        # Release information
        try:
            release_data = self.client.get_latest_release(owner, repo)
            if release_data:
                metadata.softwareVersion = release_data.get("tag_name")
                record("softwareVersion")
                if release_data.get("published_at"):
                    release_date = release_data.get("published_at")[:10]
                    try:
                        commits_data = self.client.get_commits(owner, repo, page=1)
                        if commits_data:
                            commit_date = commits_data[0]["commit"]["committer"]["date"][:10]
                            if commit_date <= release_date:
                                metadata.version = release_data.get("tag_name")
                                record("version")
                    except Exception:
                        pass
                metadata.has_release = True
        except Exception:
            metadata.has_release = False
        
        return metadata

