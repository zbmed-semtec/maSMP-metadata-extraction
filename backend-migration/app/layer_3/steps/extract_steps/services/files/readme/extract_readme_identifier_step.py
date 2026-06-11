"""Extract identifier links from README content into step state."""
from __future__ import annotations

import re

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)

DOI_URL_PATTERN = re.compile(
    r"https://(?:doi\.org/([^\s\)\]\"']+)|zenodo\.org/records?/(\d+))",
    re.IGNORECASE,
)


class ExtractReadmeIdentifierStep:
    """Extract DOI/Zenodo identifier URL without mutating metadata."""

    name = "readme.extract_identifier"

    def run(self, context: StepContext, state: StepState) -> StepState:
        content = repository_file_content(
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


__all__ = ["ExtractReadmeIdentifierStep"]

