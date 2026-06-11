"""Pipeline composer for selecting extraction profiles by context."""
from __future__ import annotations

from app.layer_3.composers.profiles.software_github_codemeta import (
    build_software_github_codemeta_pipeline,
)
from app.layer_3.composers.profiles.software_github_masmp import (
    build_software_github_masmp_pipeline,
)
from app.layer_3.composers.profiles.software_gitlab_codemeta import (
    build_software_gitlab_codemeta_pipeline,
)
from app.layer_3.composers.profiles.software_gitlab_masmp import (
    build_software_gitlab_masmp_pipeline,
)
from app.layer_3.steps.contracts.pipeline import ExtractionPipeline


class PipelineComposer:
    """
    Select extraction pipeline profile from domain/schema/platform.

    This is a minimal Phase 1 composer. Additional profiles can be added as
    we split existing Layer 3 adapters/services into fine-grained steps.
    """

    def compose(
        self,
        *,
        domain: str,
        schema: str,
        platform: str | None = None,
    ) -> ExtractionPipeline:
        if domain == "software":
            normalized_schema = schema.strip().lower()
            normalized_platform = (platform or "github").strip().lower()
            if normalized_schema == "masmp":
                if normalized_platform == "github":
                    return build_software_github_masmp_pipeline()
                if normalized_platform == "gitlab":
                    return build_software_gitlab_masmp_pipeline()
                raise ValueError(
                    f"Unsupported platform for software/maSMP: {platform!r}. "
                    "Expected one of: 'github', 'gitlab', or None."
                )
            if normalized_schema == "codemeta":
                if normalized_platform == "github":
                    return build_software_github_codemeta_pipeline()
                if normalized_platform == "gitlab":
                    return build_software_gitlab_codemeta_pipeline()
                raise ValueError(
                    f"Unsupported platform for software/codemeta: {platform!r}. "
                    "Expected one of: 'github', 'gitlab', or None."
                )
            raise ValueError(
                f"Unsupported schema for software domain: {schema!r}. "
                "Expected one of: 'maSMP', 'codemeta'."
            )

        raise ValueError(
            f"Unsupported domain for pipeline composition: {domain!r}. "
            "Add a profile under app.layer_3.composers.profiles."
        )
