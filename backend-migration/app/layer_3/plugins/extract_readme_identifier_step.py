"""Extract identifier links from README content into step state."""

import re

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.repository_files import RepositoryFilesPlugin

DOI_URL_PATTERN = re.compile(
    r"https://(?:doi\.org/([^\s\)\]\"']+)|zenodo\.org/records?/(\d+))",
    re.IGNORECASE,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractReadmeIdentifierStep(ExtractionPlugin):
    """Extract DOI/Zenodo identifier URL without mutating metadata."""

    name = "readme.extract_identifier"
    platforms = {"gitlab", "github"}
    extracts = {"identifier"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        rfp : RepositoryFilesPlugin = self.plugin_manager.get("repository-files-plugin")
        content = rfp.repository_file_content(
            context,
            state,
            "readme_content",
            ("README.md", "README.rst", "README.txt", "README"),
        )
        state.data["identifier_set_by_readme"] = False
        state.data["extracted_readme_identifier_url"] = None
        for match in DOI_URL_PATTERN.finditer(content):
            doi = match.group(1) if match.group(1) else f"10.5281/zenodo.{match.group(2)}"
            doi_url = f"https://doi.org/{doi}"
            state.data["extracted_readme_identifier_url"] = doi_url
            state.data["identifier_set_by_readme"] = True
            break
        return state




