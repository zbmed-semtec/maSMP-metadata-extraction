"""Codeberg extractor plugins for populating schema.org / codemeta / maSMP
metadata fields from a repository's Codeberg API data, CITATION.cff files,
README files, and license files."""

from app.layer_3.plugins.codeberg.codeberg_base_extractor import CodebergBaseExtractor
from app.layer_3.plugins.shared.collection import (GitPlatformDescriptionExtractor
,GitPlatformNameExtractor
,GitPlatformUrlExtractor
,GitPlatformCodeRepositoryExtractor
,GitPlatformProgrammingLanguageExtractor
,GitPlatformAuthorExtractor
,GitPlatformLicenseExtractor
,GitPlatformIdentifierExtractor
,GitPlatformCitationExtractor
,GitPlatformKeywordsExtractor
,GitPlatformReadmeExtractor
,GitPlatformVersionControlSystemExtractor
,GitPlatformArchivedAtExtractor
,GitPlatformContributorsExtractor
,GitPlatformReleaseNotesExtractor
,GitPlatformSoftwareVersionExtractor
,GitPlatformHasSourceCodeExtractor
,GitPlatformConditionsOfAccessExtractor
,GitPlatformIsAccessibleForFreeExtractor
,GitPlatformDateExtractor
,GitPlatformIssueTrackerExtractor
,GitPlatformChangelogExtractor
,GitPlatformSoftwareRequirementExtractor
,GitPlatformLicenseCopyrightHolderExtractor
,GitPlatformStorageReqExtractor
,GitPlatformDownloadUrlExtractor)

class CodebergNameExtractor(GitPlatformNameExtractor, CodebergBaseExtractor):
    """schema:name"""
    name = "codeberg.name_extractor"

class CodebergDescriptionExtractor(GitPlatformDescriptionExtractor, CodebergBaseExtractor):
    name = "codeberg.description_extractor"

class CodebergUrlExtractor(GitPlatformUrlExtractor, CodebergBaseExtractor):
    """schema:url"""
    name = "codeberg.url_extractor"

class CodebergCodeRepositoryExtractor(GitPlatformCodeRepositoryExtractor, CodebergBaseExtractor):
    """schema:codeRepository"""
    name = "codeberg.code_repository_extractor"

class CodebergProgrammingLanguageExtractor(GitPlatformProgrammingLanguageExtractor, CodebergBaseExtractor):
    """schema:programmingLanguage"""
    name = "codeberg.programming_language_extractor"

class CodebergAuthorExtractor(GitPlatformAuthorExtractor, CodebergBaseExtractor):
    """schema:author"""
    name = "codeberg.author_extractor"

class CodebergLicenseExtractor(GitPlatformLicenseExtractor, CodebergBaseExtractor):
    """schema:license"""
    name = "codeberg.license_extractor"

class CodebergIdentifierExtractor(GitPlatformIdentifierExtractor, CodebergBaseExtractor):
    """schema:identifier"""
    name = "codeberg.identifier_extractor"

class CodebergCitationExtractor(GitPlatformCitationExtractor, CodebergBaseExtractor):
    """schema:citation"""
    name = "codeberg.citation_extractor"

class CodebergKeywordsExtractor(GitPlatformKeywordsExtractor, CodebergBaseExtractor):
    """schema:keywords"""
    name = "codeberg.keywords_extractor"

class CodebergReadmeExtractor(GitPlatformReadmeExtractor, CodebergBaseExtractor):
    """codemeta:readme"""
    name = "codeberg.readme_extractor"

class CodebergVersionControlSystemExtractor(GitPlatformVersionControlSystemExtractor, CodebergBaseExtractor):
    """maSMP:versionControlSystem - hardcoded, since Codeberg is a Git-only forge"""
    name = "codeberg.version_control_system_extractor"

class CodebergArchivedAtExtractor(GitPlatformArchivedAtExtractor, CodebergBaseExtractor):
    """schema:archivedAt"""
    name = "codeberg.archived_at_extractor"

class CodebergContributorsExtractor(GitPlatformContributorsExtractor, CodebergBaseExtractor):
    name = "codeberg.contributors_extractor"

class CodebergReleaseNotesExtractor(GitPlatformReleaseNotesExtractor, CodebergBaseExtractor):
    """schema:releaseNotes"""
    name = "codeberg.release_notes_extractor"

class CodebergSoftwareVersionExtractor(GitPlatformSoftwareVersionExtractor, CodebergBaseExtractor):
    """schema:softwareVersion"""
    name = "codeberg.software_version_extractor"

class CodebergHasSourceCodeExtractor(GitPlatformHasSourceCodeExtractor, CodebergBaseExtractor):
    """maSMP:hasSourceCode"""
    name = "codeberg.has_source_code_extractor"

class CodebergConditionsOfAccessExtractor(GitPlatformConditionsOfAccessExtractor, CodebergBaseExtractor):
    """schema:conditionsOfAccess - SoftwareApplication slot, mirrors license"""
    name = "codeberg.conditions_of_access_extractor"

class CodebergIsAccessibleForFreeExtractor(GitPlatformIsAccessibleForFreeExtractor, CodebergBaseExtractor):
    """maSMP:isAccessibleForFree - SoftwareApplication slot, hardcoded to True"""
    name = "codeberg.is_accessible_for_free_extractor"

class CodebergDateExtractor(GitPlatformDateExtractor, CodebergBaseExtractor):
    """extracts creation, modification, and publication dates for a Codeberg repository,
    falling back to the latest tag's commit date if no releases exist"""
    name = "codeberg.date_extractor"

class CodebergIssueTrackerExtractor(GitPlatformIssueTrackerExtractor, CodebergBaseExtractor):
    """extracts the issue tracker URL for a Codeberg repository"""
    name = "codeberg.issue_tracker_extractor"

class CodebergChangelogExtractor(GitPlatformChangelogExtractor, CodebergBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""
    name = "codeberg.changelog_extractor"

class CodebergSoftwareRequirementExtractor(GitPlatformSoftwareRequirementExtractor, CodebergBaseExtractor):

    name = "codeberg.software_requirements_extractor"

class CodebergLicenseCopyrightHolderExtractor(GitPlatformLicenseCopyrightHolderExtractor, CodebergBaseExtractor):
    """extracts the copyright holder and year from the license file"""
    name = "codeberg.extract_copyright_year_and_holder"
    
class CodebergStorageReqExtractor(GitPlatformStorageReqExtractor, CodebergBaseExtractor):
    """extracts the copyright holder and year from the license file"""
    name = "codeberg.storage_requirement_extractor"

class CodebergDownloadUrlExtractor(GitPlatformDownloadUrlExtractor, CodebergBaseExtractor):
    """extracts the copyright holder and year from the license file"""
    name = "codeberg.codeberg_download_url_extractor"