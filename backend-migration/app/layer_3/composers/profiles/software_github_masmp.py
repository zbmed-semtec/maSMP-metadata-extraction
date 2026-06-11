"""Software + GitHub + maSMP pipeline profile."""
from __future__ import annotations

from app.layer_3.steps.contracts.pipeline import ExtractionPipeline
from app.layer_3.steps.step_bundles import (
    software_alternate_name_steps,
    software_archived_url_steps,
    software_author_steps,
    software_identifier_steps,
    software_keyword_steps,
    software_reference_publication_steps,
)
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_access_step import github_access_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_repository_property_steps import (
    github_basic_info_steps,
)
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_contributors_step import github_contributor_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_dates_step import github_date_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_download_url_step import github_download_url_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_metadata_files_step import github_readme_changelog_link_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_issue_tracker_step import github_issue_tracker_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_keywords_step import github_keyword_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_license_step import github_license_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_programming_languages_step import github_programming_language_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_release_step import github_release_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_requirements_links_step import github_requirements_link_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_source_code_step import github_source_code_steps
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_vcs_step import github_vcs_steps
from app.layer_3.steps.extract_steps.adapters.platform.common import common_platform_steps
from app.layer_3.steps.extract_steps.services.files.license import ExtractLicenseCopyrightStep
from app.layer_3.steps.merge_steps.software import MergeSoftwareCopyrightHolderStep
from app.config import readme_llm_settings
from app.layer_3.steps.extract_steps.services.files.extract_readme_orchestration_step import (
    ApplyReadmeOrchestrationStep,
)


def build_software_github_masmp_pipeline() -> ExtractionPipeline:
    return ExtractionPipeline(
        steps=(
            common_platform_steps()
            + github_basic_info_steps()
            + github_date_steps()
            + github_access_steps()
            + github_issue_tracker_steps()
            + github_download_url_steps()
            + github_source_code_steps()
            + github_keyword_steps()
            + github_vcs_steps()
            + github_programming_language_steps()
            + github_contributor_steps()
            + github_license_steps()
            + (ExtractLicenseCopyrightStep(), MergeSoftwareCopyrightHolderStep())
            + github_readme_changelog_link_steps()
            + ((ApplyReadmeOrchestrationStep(),) if readme_llm_settings.enabled else ())
            + github_requirements_link_steps()
            + github_release_steps()
            + software_identifier_steps()
            + software_alternate_name_steps()
            + software_keyword_steps()
            + software_author_steps()
            + software_reference_publication_steps()
            + software_archived_url_steps()
        )
    )
