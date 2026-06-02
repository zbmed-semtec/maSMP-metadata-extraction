"""Extract BibTeX reference data from README content into step state."""

import re

from app.layer_1.entities.shared_primitives import Person
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)


class ExtractReadmeBibtexStep(ExtractionStep):
    """Extract first BibTeX citation block without mutating metadata."""

    name = "readme.extract_bibtex"

    def run(self, context: StepContext, state: StepState) -> StepState:
        content = repository_file_content(
            context,
            state,
            "readme_content",
            ("README.md", "README.rst", "README.txt", "README"),
        )
        citations = re.findall(r"```bibtex([\s\S]*?)```", content)
        if not citations:
            return state
        citation = citations[0]
        all_authors: list[Person] = []
        title_match = re.search(r'title\s*=\s*[{"](.*?)[}"]', citation, re.IGNORECASE)
        title = title_match.group(1) if title_match else None
        author_matches = re.findall(r'author\s*=\s*[{"](.*?)[}"]', citation, re.IGNORECASE)
        authors: list[Person] = []
        for author_str in author_matches:
            for author in author_str.split(" and "):
                author_parts = author.strip().split(" ")
                author_obj = Person(
                    type="Person",
                    familyName=author_parts[0].strip() if len(author_parts) > 0 else None,
                    givenName=author_parts[1].strip() if len(author_parts) > 1 else None,
                )
                authors.append(author_obj)
                all_authors.append(author_obj)
        state.data["bibtex_title"] = title
        state.data["bibtex_authors"] = authors
        state.data["all_readme_authors"] = all_authors
        return state


__all__ = ["ExtractReadmeBibtexStep"]

