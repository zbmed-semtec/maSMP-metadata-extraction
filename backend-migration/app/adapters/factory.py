"""
Layer 3: Adapters - Factory
Factory pattern to select the correct platform extractor
"""
from typing import Optional
from app.adapters.github.github_extractor import GitHubExtractor
from app.adapters.gitlab.gitlab_extractor import GitLabExtractor
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
        elif platform == "gitlab":
            return GitLabExtractor(access_token)
        else:
            raise ValueError(f"Unsupported platform: {platform}. Supported platforms: GitHub, GitLab")

