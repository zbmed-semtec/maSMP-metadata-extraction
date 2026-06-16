"""Extract Zenodo archivedAt candidates."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)
from app.layer_3.utils.url_pattern_matcher import URLPatternMatcher


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractZenodoArchivedUrlsStep(ExtractionPlugin):
    """Extract Zenodo candidates for metadata.archivedAt."""

    name = "zenodo.extract_archived_urls"
    platforms = {"gitlab", "github"}
    extracts = {"archivedAt"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        readme_content = repository_file_content(
            context,
            state,
            "readme_content",
            ("README.md", "README.rst", "README.txt", "README"),
        )
        state.data["extracted_zenodo_archive_urls"] = _extract_zenodo_archive_urls(readme_content)
        return state


def _extract_zenodo_archive_urls(readme_content: str) -> list[str]:
    matcher = URLPatternMatcher()
    return matcher.check_zenodo_badge(readme_content) or []


__all__ = ["ExtractZenodoArchivedUrlsStep"]
