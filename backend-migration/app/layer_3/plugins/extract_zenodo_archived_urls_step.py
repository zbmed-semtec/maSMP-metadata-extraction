"""Extract Zenodo archivedAt candidates."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.repository_files import RepositoryFilesPlugin
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractZenodoArchivedUrlsStep(ExtractionPlugin):
    """Extract Zenodo candidates for metadata.archivedAt."""

    name = "zenodo.extract_archived_urls"
    platforms = {"gitlab", "github"}
    extracts = {'archivedAt'}
    priority_level = 102
    
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        rfp : RepositoryFilesPlugin = self.plugin_manager.get('repository-files-plugin')
        readme_content = rfp.repository_file_content(
            context,
            state,
            "readme_content",
            ("README.md", "README.rst", "README.txt", "README"),
        )
        state.data["extracted_zenodo_archive_urls"] = self._extract_zenodo_archive_urls(readme_content)
        return state


    def _extract_zenodo_archive_urls(self, readme_content: str) -> list[str]:
        matcher : URLPatternMatcher = self.plugin_manager.get('url-pattern-matcher-plugin')
        return matcher.check_zenodo_badge(readme_content) or []



