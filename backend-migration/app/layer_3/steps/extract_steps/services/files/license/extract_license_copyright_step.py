"""Extract copyright holder from LICENSE content into step state."""

import re

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)


class ExtractLicenseCopyrightStep:
    """Extract copyright holder from common LICENSE line formats."""

    name = "license.extract_copyright"

    def run(self, context: StepContext, state: StepState) -> StepState:
        license_content = repository_file_content(
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


__all__ = ["ExtractLicenseCopyrightStep"]

