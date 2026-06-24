"""GitHub requirements links steps."""

from app.layer_3.steps.contracts import ExtractionStep, ExtractionContext, ExtractionState
from app.layer_3.plugins.requirement_discovery_plugin import RequirementDiscoveryPlugin
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubRequirementsLinksStep(ExtractionPlugin):
    """Extract requirements links for GitHub repositories."""

    name = "github.extract_requirements_links"

    extracts = {"softwareRequirements"}

    platforms = {"github"}
    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        rdp : RequirementDiscoveryPlugin = self.plugin_manager.get("requirement-discovery-plugin")
        urls = rdp.discover_requirement_urls_from_state(
            state_data=state.data,
            platform="github",
            repo_url=context.repo_url,
        )
        if urls:
            softwareRequirements = urls
            state.metadata_collector.collect(self.name, "softwareRequirements", softwareRequirements)
        return state
