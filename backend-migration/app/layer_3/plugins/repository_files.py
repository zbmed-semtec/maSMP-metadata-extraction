"""Repository file content helpers used by file extraction steps."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin
from app.layer_2.base_plugin import BasePlugin

class RepositoryFilesPlugin(BasePlugin):
    
    name = "repository-files-plugin"

    def repository_file_content(
        self,
        context: ExtractionContext,
        state: ExtractionState,
        data_key: str,
        file_names: tuple[str, ...],
    ) -> str:
        """Return cached content for the first matching repository file."""
        cached = state.data.get(data_key)
        if cached:
            return cached

        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')

        owner, repo = ppp.repo_parts(context)
        if not owner or not repo:
            return ""

        fetcher = None
        if 'github.com' in context.repo_url:
            fetcher = ppp.github_file_fetcher(context, state)
        elif 'gitlab.com' in context.repo_url:
            fetcher = ppp.gitlab_file_fetcher(context, state)
        else:
            raise NotImplemented(f"no file fetcher known for {context.repo_url}")

        for branch in ("main", "master"):
            for file_name in file_names:
                content = fetcher.fetch_file_from_repo(owner, repo, file_name, branch)
                if content:
                    state.data[data_key] = content
                    return content
        state.data[data_key] = ""
        return ""

