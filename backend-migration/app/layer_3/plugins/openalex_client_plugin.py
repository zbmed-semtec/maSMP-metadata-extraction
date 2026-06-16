"""HTTP client for OpenAlex work lookups (shared by OpenAlex extract steps)."""
from app.layer_2.base_plugin import BasePlugin
from typing import Optional
import requests

class OpenAlexClient(BasePlugin):
    """Call OpenAlex and return raw work JSON (no domain extraction here)."""

    name = "openalex_client_plugin"

    BASE_URL = "https://api.openalex.org/works"

    def fetch_work_by_doi(self, doi: str) -> Optional[dict]:
        clean_doi = doi.replace("https://doi.org/", "").replace("doi:", "")
        url = f"{self.BASE_URL}/doi:{clean_doi}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

__all__ = ["OpenAlexClient"]
