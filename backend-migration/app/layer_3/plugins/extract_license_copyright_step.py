"""Extract copyright holder from LICENSE content into step state."""

import re

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.repository_files import RepositoryFilesPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractLicenseCopyrightStep(ExtractionPlugin):
    """Extract copyright holder from common LICENSE line formats."""

    name = "license.extract_copyright"
    platforms = {"gitlab", "github"}
    extracts = {'license', "copyrightHolder"}
    priority_level = 102

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        rfp = self.plugin_manager.get('repository-files-plugin')
        license_content = rfp.repository_file_content(
            context,
            state,
            "license_content",
            ("LICENSE", "LICENSE.md", "COPYING", "COPYING.md"),
        )
        match = re.search(r"Copyright\s+\([cC]\)\s+\d{4}\s+(.+)", license_content)
        state.data["extracted_license_copyright_holder"] = (
            match.group(1).strip() if match else None
        )
        return state




