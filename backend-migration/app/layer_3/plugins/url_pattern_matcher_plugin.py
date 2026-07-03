import re
from urllib.parse import urlparse
from typing import Optional, Tuple
from app.layer_2.base_plugin import BasePlugin

class URLPatternMatcher(BasePlugin):

    name = "url-pattern-matcher-plugin"

    @staticmethod
    def extract_repo_info(repo_url: str) -> Tuple[Optional[str], Optional[str]]:
        parsed_url = urlparse(repo_url)
        parts = parsed_url.path.strip("/").split("/")
        if len(parts) < 2:
            return None, None
        return parts[-2], parts[-1]

    @staticmethod
    def detect_platform(repo_url: str) -> Optional[str]:
        netloc = urlparse(repo_url).netloc.lower()
        if "github.com" in netloc:
            return "github"
        if "gitlab.com" in netloc:
            return "gitlab"
        return None

    @staticmethod
    def check_zenodo_badge(content: str) -> list[str]:
        zenodo_pattern = r"https://(?:doi\.org/(\d+\.\d+/zenodo\.\d+)|zenodo\.org/records?/(\d+))"
        matches = re.findall(zenodo_pattern, content)
        extracted_ids = {doi if doi else f"10.5281/zenodo.{record_id}" for doi, record_id in matches}
        return [f"https://doi.org/{doi}" for doi in extracted_ids]
