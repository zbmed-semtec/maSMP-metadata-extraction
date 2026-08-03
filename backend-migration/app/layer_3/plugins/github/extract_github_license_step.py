"""GitHub license metadata steps."""

from app.layer_1.entities.shared_primitives import License
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubLicenseStep(ExtractionPlugin):
    name = "github.extract_license"

    extracts = {"https://schema.org/license"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        payload = ppp.github_license_payload(context, state)
        license_info = payload.get("license") if isinstance(payload, dict) else None
        if license_info:
            license = License(name=license_info.get("name"), url=license_info.get("url"))
            state.metadata_collector.collect(self.name, "https://schema.org/license", license)
        return state
