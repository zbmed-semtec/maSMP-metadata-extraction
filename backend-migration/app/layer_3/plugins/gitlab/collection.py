import re
import datetime

from app.layer_3.plugins.gitlab.gitlab_client import GitLabClient
from app.layer_3.plugins.gitlab.gitlab_base_extractor import GitLabBaseExtractor
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher
from app.layer_3.plugins.shared.wayback_client import WaybackClient
from app.layer_3.plugins.shared.software_heritage_client import SoftwareHeritageClient
from app.layer_3.plugins.shared.open_alex_client import OpenAlexClient
from app.layer_3.plugins.shared.utils import match_license_text


class GitLabNameExtractor(GitLabBaseExtractor):
    """schema:name"""

    extracts = {'https://schema.org/name'}
    name = "gitlab.name_extractor"

    def extract(self, context, state):
        # getting the name from the API
        result = self.get_client(context, state).get_repository()
        if result.get("name"):
            state.metadata_collector.collect("GitLab API", "https://schema.org/name", result['name'], 0.95)

        # getting the name from the CFF
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'title' in cff:
                state.metadata_collector.collect("CFF File", "https://schema.org/name", cff['title'], 0.85)
        return state


class GitLabDescriptionExtractor(GitLabBaseExtractor):
    """schema:description"""

    extracts = {'https://schema.org/description'}
    name = "gitlab.description_extractor"

    def extract(self, context, state):
        # getting the description from the GitLab API
        result = self.get_client(context, state).get_repository()
        if result.get("description"):
            state.metadata_collector.collect("GitLab API", "https://schema.org/description", result['description'], 0.95)

        # getting the description from the CFF
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            # non standard but seen 'in the wild'
            if 'abstract' in cff:
                state.metadata_collector.collect("CFF File", "https://schema.org/description", cff['abstract'], 0.85)
            # non standard but seen 'in the wild'
            if 'description' in cff:
                state.metadata_collector.collect("CFF File", "https://schema.org/description", cff['description'], 0.85)
        return state


class GitLabUrlExtractor(GitLabBaseExtractor):
    """schema:url"""

    extracts = {'https://schema.org/url'}
    name = "gitlab.url_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get("web_url"):
            state.metadata_collector.collect("GitLab API", "https://schema.org/url", repo['web_url'], 0.95)
        return state


class GitLabProgrammingLanguageExtractor(GitLabBaseExtractor):
    """schema:programmingLanguage"""

    extracts = {'https://schema.org/programmingLanguage'}
    name = "gitlab.programming_language_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)

        # GitLab doesn't return a primary language on the project object;
        # it requires a dedicated /languages endpoint returning percentage breakdowns.
        try:
            languages = client.get_programming_languages()
            if isinstance(languages, dict) and languages:
                state.metadata_collector.collect("GitLab API", "https://schema.org/programmingLanguage", list(languages.keys()), 0.95)
        except Exception:
            pass
        return state

class GitLabKeywordsExtractor(GitLabBaseExtractor):
    """schema:keywords"""

    extracts = {'https://schema.org/keywords'}
    name = "gitlab.keywords_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        
        citations = client.get_parsed_citations()
        keywords = []
        for cff in citations:
            keywords.extend(cff.get('keywords', []))
        if len(keywords) > 0:
            state.metadata_collector.collect("CFF File", "https://schema.org/keywords", keywords, 0.85)
        
        # Query OpenAlex
        for doi in client.get_dois_from_parsed_citaitons().union(client.get_dois_from_readmes()):
            keywords = OpenAlexClient.get_or_create(context, state).get_keywords(doi)
            if len(keywords) > 0:
                state.metadata_collector.collect("OpenAlex", "https://schema.org/keywords", keywords, 0.95)
                
        return state

class GitLabAuthorExtractor(GitLabBaseExtractor):
    """schema:author"""

    extracts = {'https://schema.org/author'}
    name = "gitlab.author_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        citations = client.get_parsed_citations()
        for cff in citations:
            authors = []
            for cffAuthor in cff.get("authors", []):
                person = {"@type": "Person"}
                if "family-names" in cffAuthor:
                    person["familyName"] = cffAuthor["family-names"]
                if "given-names" in cffAuthor:
                    person["givenName"] = cffAuthor["given-names"]
                if "orcid" in cffAuthor:
                    person["@id"] = cffAuthor["orcid"]
                if 'name' in cffAuthor:
                    person["name"] = cffAuthor["name"]
                authors.append(person)
            if len(authors) > 0:
                state.metadata_collector.collect("CFF File", "https://schema.org/author", authors, 0.85)
        
        # Query OpenAlex
        for citation in client.get_parsed_citations():
            if 'doi' in citation:
                doi = citation['doi']
                authors = OpenAlexClient.get_or_create(context, state).get_authors(doi)
                if authors:
                    state.metadata_collector.collect("OpenAlex", "https://schema.org/author", authors, 0.95)
        
        return state


class GitLabLicenseExtractor(GitLabBaseExtractor):
    """schema:license"""

    extracts = {'https://schema.org/license'}
    name = "gitlab.license_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)

        # Try to get license from GitLab API first
        license_info = client.get_license()
        if license_info and isinstance(license_info, dict):
            spdx_id = license_info.get("key") or license_info.get("spdx_id")
            if spdx_id and spdx_id.upper() not in {"NOASSERTION", "OTHER"}:
                license_object = {
                    '@type': 'CreativeWork',
                    '@context': 'https://schema.org',
                    'name': spdx_id,
                    'url': f'https://spdx.org/licenses/{spdx_id}.html'
                }
                state.metadata_collector.collect("GitLab API", 'https://schema.org/license', license_object, 0.95)

        # Fallback to license candidate files
        license_candidates = client.get_license_candidate_files()
        for license_candidate in license_candidates:
            text = license_candidate.get_content()
            result = match_license_text(text)
            spdx_id = result["detected_license_expression_spdx"]
            conf = result["percentage_of_license_text"] * 0.95 / 100.0
            license_object = {
                '@type': 'CreativeWork',
                '@context': 'https://schema.org',
                'name': spdx_id,
                'url': f'https://spdx.org/licenses/{spdx_id}.html'
            }
            state.metadata_collector.collect("License File", 'https://schema.org/license', license_object, conf)

        # Check CFF for license information
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'license' in citation:
                spdx_id = citation['license']
                if spdx_id and spdx_id != "NOASSERTION":
                    license_object = {
                        '@type': 'CreativeWork',
                        '@context': 'https://schema.org',
                        'name': spdx_id,
                        'url': f'https://spdx.org/licenses/{spdx_id}.html'
                    }
                    state.metadata_collector.collect("CFF File", 'https://schema.org/license', license_object, 0.85)
            if 'license-url' in citation:
                license_url = citation['license-url']
                if license_url:
                    license_object = {
                        '@type': 'CreativeWork',
                        '@context': 'https://schema.org',
                        'url': license_url
                    }
                    state.metadata_collector.collect("CFF File", 'https://schema.org/license', license_object, 0.85)
        return state


class GitLabIdentifierExtractor(GitLabBaseExtractor):
    """schema:identifier"""

    extracts = {'https://schema.org/identifier'}
    name = "gitlab.identifier_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        
        # from CFF
        citations = client.get_parsed_citations()
        for cff in citations:
            identifiers = []
            for cffIdentifier in cff.get("identifiers", []):
                if cffIdentifier.get("type") == "doi" and cffIdentifier.get("value"):
                    doi_url = f"https://doi.org/{cffIdentifier['value']}"
                    identifiers.append(doi_url)
            doi = cff.get("doi")
            if doi:
                doi_url = f"https://doi.org/{doi}"
                identifiers.append(doi_url)
            if len(identifiers) > 0:
                state.metadata_collector.collect("CFF File", "https://schema.org/identifier", identifiers, 0.85)

        # from README
        readmes = client.get_readme_candidate_files()
        for readme in readmes:
            readme_content = readme.get_content()
            if readme_content:
                doi_candidates = URLPatternMatcher.check_zenodo_badge(readme_content)
                for doi_url in doi_candidates:
                    state.metadata_collector.collect("README", "https://schema.org/identifier", doi_url, 0.6)
        return state


class GitLabCitationExtractor(GitLabBaseExtractor):
    """schema:citation - derived from a CFF file's preferred-citation entry"""

    extracts = {'https://schema.org/citation'}
    name = "gitlab.citation_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        citations = client.get_parsed_citations()
        for cff in citations:
            preferred_citation = cff.get("preferred-citation")
            if preferred_citation and isinstance(preferred_citation, dict):
                citation_entry = {"@type": "Article"}
                doi_value = preferred_citation.get("doi")
                if doi_value:
                    doi_url = f"https://doi.org/{str(doi_value)}"
                    citation_entry["@id"] = doi_url
                title = preferred_citation.get("title")
                if title:
                    citation_entry["title"] = str(title)
                    state.metadata_collector.collect("CFF File", "https://schema.org/alternateName", str(title), 0.85)
                authors_field = preferred_citation.get("authors") or []
                author_list: list[dict] = []
                for author in authors_field:
                    if not isinstance(author, dict):
                        continue
                    given = author.get("given-names")
                    family = author.get("family-names")
                    if not given and not family and not author.get("orcid"):
                        continue
                    person: dict[str, str] = {"@type": "Person"}
                    if given:
                        person["givenName"] = given
                    if family:
                        person["familyName"] = family
                    if author.get("orcid"):
                        person["@id"] = author["orcid"]
                    author_list.append(person)
                if author_list:
                    citation_entry["author"] = author_list
                state.metadata_collector.collect("CFF File", "https://schema.org/citation", citation_entry, 0.85)
        return state


class GitLabReadmeExtractor(GitLabBaseExtractor):
    """codemeta:readme"""

    extracts = {'https://codemeta.gitLab.io/terms/readme'}
    name = "gitlab.readme_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()        
        if 'readme_url' in repo:
            state.metadata_collector.collect("GitLab API", "https://codemeta.gitLab.io/terms/readme", repo['readme_url'], 0.95)
        return state


class GitLabVersionControlSystemExtractor(GitLabBaseExtractor):
    """maSMP:versionControlSystem - hardcoded, since GitLab is a Git-only forge"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/versionControlSystem'}
    name = "gitlab.version_control_system_extractor"

    def extract(self, context, state):
        state.metadata_collector.collect("Constant", "https://discovery.biothings.io/ns/maSMP/versionControlSystem", "git", 0.99)
        return state


class GitLabContributorsExtractor(GitLabBaseExtractor):
    """schema:contributor"""

    extracts = {'https://schema.org/contributor'}
    name = "gitlab.contributors_extractor"

    def extract(self, context, state):
        try:
            client = self.get_client(context, state)
            result = client.get_contributors()
            contributors = []
            if isinstance(result, list):
                for contributor in result:
                    person = {
                        '@type': 'Person',
                        '@context': 'https://schema.org',
                        'name': contributor.get('name', ''),
                        'contributions': contributor.get('commits', 0)
                    }
                    # GitLab contributor objects don't include a profile URL or
                    # login handle, only name/email/commits/additions/deletions,
                    # so no 'url' field can be populated here (unlike GitLab's html_url).
                    contributors.append(person)
            if contributors:
                state.metadata_collector.collect("GitLab API", "https://schema.org/contributor", contributors, 0.95)
        except Exception:
            pass
        return state


class GitLabReleaseNotesExtractor(GitLabBaseExtractor):
    """schema:releaseNotes"""

    extracts = {'https://schema.org/releaseNotes', 'https://codemeta.gitLab.io/terms/releaseNotes'}
    name = "gitlab.release_notes_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        try:
            releases = client.get_releases()
            if isinstance(releases, list) and len(releases) > 0:
                latest_release = releases[0]
                description = latest_release.get("description")
                if description:
                    state.metadata_collector.collect("GitLab API", "https://schema.org/releaseNotes", description, 0.95)
                    state.metadata_collector.collect("GitLab API", "https://codemeta.gitLab.io/terms/releaseNotes", description, 0.95)
        except Exception:
            pass
        return state


class GitLabVersionExtractor(GitLabBaseExtractor):
    """schema:softwareVersion / schema:version"""

    extracts = {'https://schema.org/softwareVersion', 'https://schema.org/version'}
    name = "gitlab.version_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)

        try:
            result = client.get_releases()
            if isinstance(result, list) and len(result) > 0:
                latest_release = result[0]
                tag_name = latest_release.get("tag_name")
                if tag_name:
                    state.metadata_collector.collect("GitLab API", "https://schema.org/softwareVersion", tag_name, 0.95)
                    state.metadata_collector.collect("GitLab API", "https://schema.org/version", tag_name, 0.95)
        except Exception:
            # Fallback to tags if no releases
            try:
                tags = client.get_tags()
                if isinstance(tags, list) and len(tags) > 0:
                    tag_name = tags[0].get("name")
                    if tag_name:
                        state.metadata_collector.collect("GitLab API", "https://schema.org/softwareVersion", tag_name, 0.85)
                        state.metadata_collector.collect("GitLab API", "https://schema.org/version", tag_name, 0.85)
            except Exception:
                pass

        # Check CFF for version
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'version' in citation:
                state.metadata_collector.collect("CFF File", "https://schema.org/softwareVersion", citation['version'], 0.85)
                state.metadata_collector.collect("CFF File", "https://schema.org/version", citation['version'], 0.85)
        return state


class GitLabHasSourceCodeExtractor(GitLabBaseExtractor):
    """maSMP:hasSourceCode"""

    extracts = {'https://codemeta.gitLab.io/terms/hasSourceCode'}
    name = "gitlab.has_source_code_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if 'web_url' in repo:
            has_source_code_url = repo['web_url']
            state.metadata_collector.collect("GitLab API", "https://codemeta.gitLab.io/terms/hasSourceCode", has_source_code_url, 0.95)
        return state


class GitLabConditionsOfAccessExtractor(GitLabBaseExtractor):
    """schema:conditionOfAccess - SoftwareApplication slot, mirrors license"""

    extracts = {'https://schema.org/conditionOfAccess'}
    name = "gitlab.conditions_of_access_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        license_info = client.get_license()
        if license_info and isinstance(license_info, dict):
            license_url = license_info.get("html_url") or license_info.get("key")
            if license_url:
                state.metadata_collector.collect("GitLab API", "https://schema.org/conditionOfAccess", license_url, 0.95)
        return state


class GitLabIsAccessibleForFreeExtractor(GitLabBaseExtractor):
    """maSMP:isAccessibleForFree - SoftwareApplication slot, based on repository visibility"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/isAccessibleForFree'}
    name = "gitlab.is_accessible_for_free_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        is_public = repo.get("visibility") == "public"
        state.metadata_collector.collect("GitLab API", "https://discovery.biothings.io/ns/maSMP/isAccessibleForFree", is_public, 0.9)
        return state


class GitLabDateExtractor(GitLabBaseExtractor):
    """schema:dateCreated / schema:dateModified / schema:datePublished"""

    extracts = {'https://schema.org/dateCreated', 'https://schema.org/dateModified', 'https://schema.org/datePublished'}
    name = "gitlab.date_extractor"

    def extract(self, context, state):
        def iso_dt_to_str(iso_dt):
            return str(datetime.datetime.fromisoformat(iso_dt.replace('Z', '+00:00')).date())

        client = self.get_client(context, state)
        repo = client.get_repository()

        if "created_at" in repo:
            state.metadata_collector.collect("GitLab API", 'https://schema.org/dateCreated', iso_dt_to_str(repo['created_at']), 0.95)
        if 'last_activity_at' in repo:
            state.metadata_collector.collect("GitLab API", 'https://schema.org/dateModified', iso_dt_to_str(repo['last_activity_at']), 0.95)

        try:
            releases = client.get_releases()
            if isinstance(releases, list) and len(releases) > 0:
                latest_release = releases[0]
                if 'released_at' in latest_release:
                    state.metadata_collector.collect("GitLab API", 'https://schema.org/datePublished', iso_dt_to_str(latest_release['released_at']), 0.85)
        except Exception:
            # Fallback to tags
            try:
                tags = client.get_tags()
                if isinstance(tags, list) and len(tags) > 0:
                    latest_tag = tags[0]
                    commit_date = latest_tag.get('commit', {}).get('created_at')
                    if commit_date:
                        state.metadata_collector.collect("GitLab API", 'https://schema.org/datePublished', iso_dt_to_str(commit_date), 0.6)
            except Exception:
                pass

        # Check CFF for release date
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'date-released' in citation:
                state.metadata_collector.collect('CFF File', 'https://schema.org/datePublished', citation['date-released'], 0.85)
        return state


class GitLabIssueTrackerExtractor(GitLabBaseExtractor):
    """extracts the issue tracker URL for a GitLab repository"""

    extracts = {'https://schema.org/issueTracker', 'https://codemeta.gitLab.io/terms/issueTracker'}
    name = "gitlab.issue_tracker_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('issues_enabled', False) and 'web_url' in repo:
            issue_tracker_url = f"{repo['web_url']}/-/issues"
            state.metadata_collector.collect("GitLab API", 'https://schema.org/issueTracker', issue_tracker_url, 0.95)
            state.metadata_collector.collect("GitLab API", 'https://codemeta.gitLab.io/terms/issueTracker', issue_tracker_url, 0.95)
        return state


class GitLabChangelogExtractor(GitLabBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/changeLog'}
    name = "gitlab.changelog_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()

        # Try to get changelog from releases
        try:
            if 'web_url' in repo:
                changelog_url = f"{repo['web_url']}/-/releases"
                state.metadata_collector.collect("Pattern", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.75)
        except Exception:
            pass

        # Look for CHANGELOG file
        try:
            urls=set()
            for candidate in client.discover_changelog_candidates():
                if 'path' in candidate:
                    url = f"https://gitlab.com/{client.get_repository_owner()}/{client.get_repository_name()}/-/raw/{client.get_default_branch()}/{candidate['path']}?ref_type=heads"
                    urls.add(url)
            if len(urls) > 0:
                state.metadata_collector.collect("Changelog File", "https://discovery.biothings.io/ns/maSMP/changeLog", list(urls))
        except Exception:
            pass
        return state


class GitLabSoftwareRequirementExtractor(GitLabBaseExtractor):
    """schema:softwareRequirements"""

    extracts = {'https://schema.org/softwareRequirements'}
    name = "gitlab.software_requirements_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        try:
            files = client.list_contents()
            found = []
            default_branch = repo.get("default_branch", "main")
            web_url = repo.get("web_url", "")
            for file in files:
                if file.get('name', '').lower() in dependency_files:
                    file_path = file.get('path')
                    if file_path:
                        raw_url = f"{web_url}/-/raw/{default_branch}/{file_path}"
                        found.append(raw_url)
            if len(found) > 0:
                state.metadata_collector.collect("GitLab API", 'https://schema.org/softwareRequirements', found, 0.95)
        except Exception:
            pass
        return state


class GitLabArchivedAtExtractor(GitLabBaseExtractor):
    """schema:archivedAt"""

    extracts = {'https://schema.org/archivedAt'}
    name = "gitlab.archived_at_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        zenodoUrls = set()
        for file in client.get_readme_candidate_files():
            readme_content = file.get_content()
            if readme_content:
                candidates = URLPatternMatcher.check_zenodo_badge(readme_content)
                for url in candidates:
                    zenodoUrls.add(url)
        if zenodoUrls:
            state.metadata_collector.collect("README", "https://schema.org/archivedAt", list(zenodoUrls), 0.6)
        
        waybackUrl = WaybackClient.get_or_create(context, state).get_archive_url()
        if waybackUrl:
            state.metadata_collector.collect("Wayback API", "https://schema.org/archivedAt", [waybackUrl], 0.95)

        softwareHeritageUrl = SoftwareHeritageClient.get_or_create(context, state).get_archive_url()
        if softwareHeritageUrl:
            state.metadata_collector.collect("Software Heritage API", "https://schema.org/archivedAt", [softwareHeritageUrl], 0.95)

        return state

class GitLabLicenseCopyrightHolderExtractor(GitLabBaseExtractor):
    """extracts the copyright holder and year from the license file"""

    name = "gitlab.extract_copyright_year_and_holder"
    extracts = {"https://schema.org/copyrightHolder", "https://schema.org/copyrightYear"}

    def extract(self, context, state):
        pattern = re.compile(
            r'Copyright\s*(?:\(c\)|©|\(C\))?\s*'
            r'(\d{4}(?:\s*[-–,]\s*\d{4})*)\s*,?\s*'
            r'([^\n\r]+?)'
            r'(?:\s*\.?\s*(?:[Aa]ll [Rr]ights [Rr]eserved\.?)?)?$',
            re.MULTILINE | re.IGNORECASE
        )

        def extract_copyright_holder(text) -> tuple[str, str]:
            match = pattern.search(text)
            if match:
                year, holder = match.groups()
                return year, holder
            return None, None

        client = self.get_client(context, state)
        try:
            licenses = client.get_license_candidate_files()
            for license_file in licenses:
                year, holder = extract_copyright_holder(license_file.get("content", ""))
                if holder:
                    state.metadata_collector.collect("License File", "https://schema.org/copyrightHolder", holder.strip(), 0.85)
                if year:
                    try:
                        year = int(year)
                        state.metadata_collector.collect("License File", "https://schema.org/copyrightYear", year, 0.85)
                    except Exception:
                        pass
        except Exception:
            pass
        return state


class GitLabStorageRequirementExtractor(GitLabBaseExtractor):
    """extracts storage requirements from repository size"""

    name = "gitlab.storage_requirement_extractor"
    extracts = {"https://schema.org/storageRequirements"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        try:
            # GitLab exposes repository size (in bytes) via the /statistics
            # endpoint, requires the `statistics=true` query param on the
            # project fetch, unlike GitLab which returns size in KB directly
            # on the base repository object.
            repo = client.get_repository()
            statistics = repo.get("statistics", {})
            repo_size_bytes = statistics.get("repository_size")
            if repo_size_bytes is not None:
                size_mb = round(repo_size_bytes / (1024 * 1024), 2)
                state.metadata_collector.collect("GitLab API", "https://schema.org/storageRequirements", f"{size_mb} MB", 0.85)
        except Exception:
            pass
        return state


class GitLabForksCountExtractor(GitLabBaseExtractor):
    """extracts the number of forks for a GitLab repository"""

    name = "gitlab.forks_count_extractor"
    extracts = {"https://codemeta.gitLab.io/terms/forks"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        forks_count = repo.get('forks_count', 0)
        if forks_count >= 0:
            state.metadata_collector.collect("GitLab API", "https://codemeta.gitLab.io/terms/forks", forks_count, 0.95)
        return state