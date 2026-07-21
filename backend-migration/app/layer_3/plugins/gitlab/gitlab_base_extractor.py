from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts.step import ExtractionContext, ExtractionState
from app.layer_3.plugins.gitlab.gitlab_client import GitLabClient

class GitLabBaseExtractor(ExtractionPlugin):
    """Base extractor class for GitLab-hosted repositories.

    Provides common functionality for extracting metadata and content from GitLab repositories,
    including client initialization and caching.
    """

    platforms = {'gitlab.com'}
    name = "please.specify.plugin.name"
    extracts = {'please.specify.what.is.being.extracted'}

    def get_client(self, context: ExtractionContext, state: ExtractionState) -> GitLabClient:
        """Gets or creates a GitLab API client instance.

        The client is cached in the extraction state to avoid recreating it for multiple operations.

        Args:
            context: Extraction context containing repository URL and access token
            state: Extraction state for caching the client instance

        Returns:
            GitLabClient: A cached GitLab API client instance
        """
        if not state.data.get('de.zbmed.gitlab.client'):
            state.data['de.zbmed.gitlab.client'] = GitLabClient(context, state)
        return state.data['de.zbmed.gitlab.client']