from app.layer_3.plugins.gitlab.gitlab_base_extractor import GitLabBaseExtractor
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

class GitLabNameExtractor(GitPlatformNameExtractor, GitLabBaseExtractor):
    """schema:name"""
    name = "gitlab.name_extractor"
    
class GitLabDescriptionExtractor(GitPlatformDescriptionExtractor, GitLabBaseExtractor):
    """schema:description"""
    name = "gitlab.description_extractor"
    
class GitLabUrlExtractor(GitPlatformUrlExtractor, GitLabBaseExtractor):
    """schema:url"""
    name = "gitlab.url_extractor"

class GitLabCloneUrlExtractor(GitPlatformCodeRepositoryExtractor, GitLabBaseExtractor):
    """schema:codeRepository"""
    name = 'gitlab.code_repository_extractor'
    
class GitLabProgrammingLanguageExtractor(GitPlatformProgrammingLanguageExtractor, GitLabBaseExtractor):
    """schema:programmingLanguage"""
    name = "gitlab.programming_language_extractor"

class GitLabKeywordsExtractor(GitPlatformKeywordsExtractor, GitLabBaseExtractor):
    """schema:keywords"""
    name = "gitlab.keywords_extractor"

class GitLabAuthorExtractor(GitPlatformAuthorExtractor, GitLabBaseExtractor):
    """schema:author"""
    name = "gitlab.author_extractor"

class GitLabLicenseExtractor(GitPlatformLicenseExtractor, GitLabBaseExtractor):
    """schema:license"""
    name = "gitlab.license_extractor"

class GitLabIdentifierExtractor(GitPlatformIdentifierExtractor, GitLabBaseExtractor):
    """schema:identifier"""
    name = "gitlab.identifier_extractor"

class GitLabCitationExtractor(GitPlatformCitationExtractor, GitLabBaseExtractor):
    """schema:citation - derived from a CFF file's preferred-citation entry"""
    name = "gitlab.citation_extractor"

class GitLabReadmeExtractor(GitPlatformReadmeExtractor, GitLabBaseExtractor):
    """codemeta:readme"""
    name = "gitlab.readme_extractor"

class GitLabVersionControlSystemExtractor(GitPlatformVersionControlSystemExtractor, GitLabBaseExtractor):
    """maSMP:versionControlSystem - hardcoded, since GitLab is a Git-only forge"""
    name = "gitlab.version_control_system_extractor"

class GitLabContributorsExtractor(GitPlatformContributorsExtractor, GitLabBaseExtractor):
    """schema:contributor"""
    name = "gitlab.contributors_extractor"

class GitLabReleaseNotesExtractor(GitPlatformReleaseNotesExtractor, GitLabBaseExtractor):
    """schema:releaseNotes"""
    name = "gitlab.release_notes_extractor"

class GitLabVersionExtractor(GitPlatformSoftwareVersionExtractor, GitLabBaseExtractor):
    """schema:softwareVersion / schema:version"""
    name = "gitlab.version_extractor"

class GitLabHasSourceCodeExtractor(GitPlatformHasSourceCodeExtractor, GitLabBaseExtractor):
    """maSMP:hasSourceCode"""
    name = "gitlab.has_source_code_extractor"

class GitLabConditionsOfAccessExtractor(GitPlatformConditionsOfAccessExtractor, GitLabBaseExtractor):
    """schema:conditionOfAccess - SoftwareApplication slot, mirrors license"""
    name = "gitlab.conditions_of_access_extractor"

class GitLabIsAccessibleForFreeExtractor(GitPlatformIsAccessibleForFreeExtractor, GitLabBaseExtractor):
    """maSMP:isAccessibleForFree - SoftwareApplication slot, based on repository visibility"""
    name = "gitlab.is_accessible_for_free_extractor"

class GitLabDateExtractor(GitPlatformDateExtractor, GitLabBaseExtractor):
    """schema:dateCreated / schema:dateModified / schema:datePublished"""
    name = "gitlab.date_extractor"

class GitLabIssueTrackerExtractor(GitPlatformIssueTrackerExtractor, GitLabBaseExtractor):
    """extracts the issue tracker URL for a GitLab repository"""
    name = "gitlab.issue_tracker_extractor"

class GitLabChangelogExtractor(GitPlatformChangelogExtractor, GitLabBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""
    name = "gitlab.changelog_extractor"

class GitLabSoftwareRequirementExtractor(GitPlatformSoftwareRequirementExtractor, GitLabBaseExtractor):
    """schema:softwareRequirements"""
    name = "gitlab.software_requirements_extractor"

class GitLabArchivedAtExtractor(GitPlatformArchivedAtExtractor, GitLabBaseExtractor):
    """schema:archivedAt"""
    name = "gitlab.archived_at_extractor"

class GitLabLicenseCopyrightHolderExtractor(GitPlatformLicenseCopyrightHolderExtractor, GitLabBaseExtractor):
    """extracts the copyright holder and year from the license file"""
    name = "gitlab.extract_copyright_year_and_holder"
    
class GitLabStorageRequirementExtractor(GitPlatformStorageReqExtractor, GitLabBaseExtractor):
    """extracts storage requirements from repository size"""
    name = "gitlab.storage_requirement_extractor"