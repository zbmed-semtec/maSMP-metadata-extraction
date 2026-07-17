from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts.step import ExtractionContext, ExtractionState
from app.layer_3.plugins.github.github_client import GitHubClient

class GitHubBaseExtractor(ExtractionPlugin):
    """Base extractor class for GitHub-hosted repositories.
    
    Provides common functionality for extracting metadata and content from GitHub repositories,
    including client initialization and caching.
    """

    platforms = {'github.com'}
    name = "please.specify.plugin.name"
    extracts = {'please.specify.what.is.being.extracted'}

    def get_client(self, context: ExtractionContext, state: ExtractionState) -> GitHubClient:
        """Gets or creates a GitHub API client instance.
        
        The client is cached in the extraction state to avoid recreating it for multiple operations.
        
        Args:
            context: Extraction context containing repository URL and access token
            state: Extraction state for caching the client instance
        
        Returns:
            GitHubClient: A cached GitHub API client instance
        """
        if not state.data.get('de.zbmed.github.client'):
            state.data['de.zbmed.github.client'] = GitHubClient(context, state)
        return state.data['de.zbmed.github.client']