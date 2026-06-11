"""Software + GitLab + CodeMeta pipeline profile."""
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
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_access_step import gitlab_access_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_repository_property_steps import (
    gitlab_basic_info_steps,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_contributors_step import gitlab_contributor_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_dates_step import gitlab_date_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_download_url_step import gitlab_download_url_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_metadata_files_step import gitlab_readme_changelog_link_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_issue_tracker_step import gitlab_issue_tracker_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_keywords_step import gitlab_keyword_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_license_step import gitlab_license_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_programming_languages_step import gitlab_programming_language_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_release_step import gitlab_release_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_requirements_links_step import gitlab_requirements_link_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_source_code_step import gitlab_source_code_steps
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_vcs_step import gitlab_vcs_steps
from app.layer_3.steps.extract_steps.adapters.platform.common import common_platform_steps
from app.layer_3.steps.extract_steps.services.files.license import ExtractLicenseCopyrightStep
from app.layer_3.steps.merge_steps.software import MergeSoftwareCopyrightHolderStep


def build_software_gitlab_codemeta_pipeline() -> ExtractionPipeline:
    return ExtractionPipeline(
        steps=(
            common_platform_steps()
            + gitlab_basic_info_steps()
            + gitlab_date_steps()
            + gitlab_access_steps()
            + gitlab_issue_tracker_steps()
            + gitlab_download_url_steps()
            + gitlab_source_code_steps()
            + gitlab_keyword_steps()
            + gitlab_vcs_steps()
            + gitlab_programming_language_steps()
            + gitlab_contributor_steps()
            + gitlab_license_steps()
            + (ExtractLicenseCopyrightStep(), MergeSoftwareCopyrightHolderStep())
            + gitlab_readme_changelog_link_steps()
            + gitlab_requirements_link_steps()
            + gitlab_release_steps()
            + software_identifier_steps()
            + software_alternate_name_steps()
            + software_keyword_steps()
            + software_author_steps()
            + software_reference_publication_steps()
            + software_archived_url_steps()
        )
    )
