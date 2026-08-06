"""Gitlab steps derived from the repo payload (name, description, url, etc.)."""
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin
from app.layer_2.extraction_plugin import ExtractionPlugin

class ExtractGitlabRepoFieldsStep(ExtractionPlugin):
    name = "gitlab.extract_repo_fields" 
    extracts = {
        "https://schema.org/conditionOfAccess",
        "https://schema.org/isAccessibleForFree",
        "https://schema.org/codeRepository",
        "dateCreated",
        "https://schema.org/dateModified",
        "https://schema.org/datePublished",
        "downloadUrl",
        "https://schema.org/issueTracker",
        "https://codemeta.github.io/terms/issueTracker", 
        "https://schema.org/discussionUrl",
        "https://schema.org/description",
        "https://schema.org/name",
        "https://schema.org/url",
        "https://codemeta.github.io/terms/hasSourceCode",
    }

    platforms = {"gitlab"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp: PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = ppp.gitlab_repo_payload(context, state)
 
        is_private = bool(repo_data.get("private", False))
        state.metadata_collector.collect(
            "gitlab.extract_access", "https://schema.org/conditionOfAccess",
            "Private" if is_private else "Public")
        state.metadata_collector.collect(
            "gitlab.extract_access", "https://schema.org/isAccessibleForFree", not is_private)
 
        html_url = repo_data.get("html_url")
 
        if html_url:
            state.metadata_collector.collect(
                "gitlab.extract_code_repository", "https://schema.org/codeRepository", f"{html_url}.git")
 
        if repo_data.get("created_at"):
            state.metadata_collector.collect(
                "gitlab.extract_dates", "dateCreated", repo_data.get("created_at"))
        if repo_data.get("updated_at"):
            state.metadata_collector.collect(
                "gitlab.extract_dates", "https://schema.org/dateModified", repo_data.get("updated_at"))
        if repo_data.get("pushed_at"):
            state.metadata_collector.collect(
                "gitlab.extract_dates", "https://schema.org/datePublished", repo_data.get("pushed_at"))
 
        archive_url = repo_data.get("archive_url", "")
        if archive_url:
            download_url = archive_url.replace("{archive_format}{/ref}", "zipball/master")
            state.metadata_collector.collect(
                "gitlab.extract_download_url", "downloadUrl", download_url)
 
        if html_url:
            state.metadata_collector.collect(
                "gitlab.extract_issue_tracker", "https://schema.org/issueTracker", f"{html_url}/issues")
            if repo_data.get("has_discussions"):
                state.metadata_collector.collect(
                    "gitlab.extract_issue_tracker", "https://schema.org/discussionUrl", f"{html_url}/discussions")
 
        description = repo_data.get("description")
        if description is not None:
            state.metadata_collector.collect(
                "gitlab.extract_repository_description", "https://schema.org/description", description)
 
        repo_name = repo_data.get("name")
        if repo_name is not None:
            state.metadata_collector.collect(
                "gitlab.extract_repository_name", "https://schema.org/name", repo_name)
 
        if html_url is not None:
            state.metadata_collector.collect(
                "gitlab.extract_repository_web_url", "https://schema.org/url", html_url)
 
        if html_url:
            state.metadata_collector.collect(
                "gitlab.extract_source_code", "https://codemeta.github.io/terms/hasSourceCode", f"{html_url}#id")
 
        return state