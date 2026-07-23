"""GitHub extractor plugins for populating schema.org / codemeta / maSMP
metadata fields from a repository's GitHub API data, CITATION.cff files,
README files, and license files."""

import re
import datetime

from app.layer_3.plugins.github.github_client import GitHubClient
from app.layer_3.plugins.github.github_base_extractor import GitHubBaseExtractor
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher
from app.layer_3.plugins.shared.wayback_client import WaybackClient
from app.layer_3.plugins.shared.software_heritage_client import SoftwareHeritageClient
from app.layer_3.plugins.shared.open_alex_client import OpenAlexClient
from app.layer_3.plugins.shared.utils import match_license_text


class GitHubNameExtractor(GitHubBaseExtractor):
    """schema:name"""

    extracts = {'https://schema.org/name'}
    name = "github.name_extractor"

    def extract(self, context, state):
        # getting the name from the API
        result = self.get_client(context, state).get_repository()
        if result.get("name"):
            state.metadata_collector.collect("GitHub API", "https://schema.org/name", result['name'], 0.95)

        # getting the name from the CFF
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'title' in cff:
                state.metadata_collector.collect("CFF File", "https://schema.org/name", cff['title'], 0.85)
        return state


class GitHubDescriptionExtractor(GitHubBaseExtractor):
    """schema:description"""

    extracts = {'https://schema.org/description'}
    name = "github.description_extractor"

    def extract(self, context, state):
        # getting the description from the GitHub API
        result = self.get_client(context, state).get_repository()
        if result.get("description"):
            state.metadata_collector.collect("GitHub API", "https://schema.org/description", result['description'], 0.95)

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


class GitHubUrlExtractor(GitHubBaseExtractor):
    """schema:url"""

    extracts = {'https://schema.org/url'}
    name = "github.url_extractor"

    def extract(self, context, state):
        # getting the URL from the GitHub API
        result = self.get_client(context, state).get_repository()
        if result.get("html_url"):
            state.metadata_collector.collect("GitHub API", "https://schema.org/url", result['html_url'], 0.95)
        # getting the URL from CITATION.cff
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'url' in cff:
                state.metadata_collector.collect("CFF File", 'https://schema.org/url', cff['url'], 0.85)
        return state


class GitHubCodeRepositoryExtractor(GitHubBaseExtractor):
    """schema:codeRepository"""

    extracts = {'https://schema.org/codeRepository', 'https://codemeta.github.io/terms/codeRepository'}
    name = "github.code_repository_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        clone_url = result.get("clone_url") or result.get("html_url")
        if clone_url:
            state.metadata_collector.collect("GitHub API", "https://schema.org/codeRepository", clone_url, 0.95)
            state.metadata_collector.collect("GitHub API", 'https://codemeta.github.io/terms/codeRepository', clone_url, 0.95)
        return state


class GitHubProgrammingLanguageExtractor(GitHubBaseExtractor):
    """schema:programmingLanguage"""

    extracts = {'https://schema.org/programmingLanguage'}
    name = "github.programming_language_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)

        # GitHub's dedicated /languages endpoint returns all detected
        # languages with their byte counts, not just the single primary
        # language exposed on the repository object.
        try:
            languages = client.get_languages()
        except Exception:
            languages = None

        if isinstance(languages, dict) and languages:
            # Sort by byte count descending, so the primary language comes first
            sorted_languages = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)
            language_names = [lang for lang, _ in sorted_languages]
            state.metadata_collector.collect("GitHub API", "https://schema.org/programmingLanguage", language_names, 0.95)
        else:
            # Fallback to the single primary language field on the repository object
            result = client.get_repository()
            primary_language = result.get("language")
            if primary_language:
                state.metadata_collector.collect("GitHub API", "https://schema.org/programmingLanguage", [primary_language], 0.85)
        return state


class GitHubAuthorExtractor(GitHubBaseExtractor):
    """schema:author"""

    extracts = {'https://schema.org/author'}
    name = "github.author_extractor"

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
        for doi in client.get_dois_from_parsed_citaitons().union(client.get_dois_from_readmes()):
            authors = OpenAlexClient.get_or_create(context, state).get_authors(doi)
            if authors:
                state.metadata_collector.collect("OpenAlex", "https://schema.org/author", authors, 0.95)
        
        return state


class GitHubLicenseExtractor(GitHubBaseExtractor):
    """schema:license"""

    extracts = {'https://schema.org/license'}
    name = "github.license_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)

        # Try to get license from GitHub API first
        result = client.get_repository()
        license_info = result.get("license")
        if license_info and isinstance(license_info, dict):
            spdx_id = license_info.get("spdx_id")
            if spdx_id and spdx_id != "NOASSERTION":
                license_object = {
                    '@type': 'CreativeWork',
                    '@context': 'https://schema.org',
                    'name': spdx_id,
                    'url': f'https://spdx.org/licenses/{spdx_id}.html'
                }
                state.metadata_collector.collect("GitHub API", 'https://schema.org/license', license_object, 0.95)

        # Fallback to license candidate files
        license_candidates = client.get_license_candidate_files()
        for license_candidate in license_candidates:
            text = license_candidate.get("content")
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


class GitHubIdentifierExtractor(GitHubBaseExtractor):
    """schema:identifier"""

    extracts = {'https://schema.org/identifier'}
    name = "github.identifier_extractor"

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
            readme_content = readme.get("content")
            if readme_content:
                doi_candidates = URLPatternMatcher.check_zenodo_badge(readme_content)
                for doi_url in doi_candidates:
                    state.metadata_collector.collect("README", "https://schema.org/identifier", doi_url, 0.6)
        return state


class GitHubCitationExtractor(GitHubBaseExtractor):
    """schema:citation"""

    extracts = {'https://schema.org/citation', "https://schema.org/alternateName", "https://codemeta.github.io/terms/referencePublication"}
    name = "github.citation_extractor"

    def _build_citation_entry(self, ref: dict) -> dict:
        """Build a citation entry (@type Article/Software/etc) from a CFF reference-like dict."""
        ref_type = ref.get("type")
        type_map = {
            "article": "Article",
            "software": "SoftwareApplication",
            "book": "Book",
            "conference-paper": "Article",
            "dataset": "Dataset",
        }
        citation_entry = {"@type": type_map.get(ref_type, "CreativeWork")}

        doi_value = ref.get("doi")
        if doi_value:
            citation_entry["@id"] = f"https://doi.org/{str(doi_value)}"

        title = ref.get("title")
        if title:
            citation_entry["title"] = str(title)

        authors_field = ref.get("authors") or []
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

        return citation_entry

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
                state.metadata_collector.collect("CFF File", "https://codemeta.github.io/terms/referencePublication", citation_entry, 0.85)
            else:
                # If no preferred-citation, we can still try to extract a DOI from the CFF file
                doi_value = cff.get("doi")
                if doi_value:
                    doi_url = f"https://doi.org/{str(doi_value)}"
                    # citation_entry = {"@type": "Software", "@id": doi_url}
                    citation_entry = doi_url
                    state.metadata_collector.collect("CFF File", "https://codemeta.github.io/terms/referencePublication", citation_entry, 0.85)

            # Extract 'references' field from CFF (list of related works/citations)
            references_field = cff.get("references") or []
            for ref in references_field:
                if not isinstance(ref, dict):
                    continue
                ref_citation_entry = self._build_citation_entry(ref)
                state.metadata_collector.collect("CFF File", "https://schema.org/citation", ref_citation_entry, 0.85)

        return state


class GitHubKeywordsExtractor(GitHubBaseExtractor):
    """schema:keywords"""

    extracts = {'https://schema.org/keywords'}
    name = "github.keywords_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        topics = result.get("topics", [])
        if topics:
            state.metadata_collector.collect("GitHub API", "https://schema.org/keywords", topics, 0.95)
        
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


class GitHubReadmeExtractor(GitHubBaseExtractor):
    """codemeta:readme"""

    extracts = {'https://codemeta.github.io/terms/readme'}
    name = "github.readme_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        readmes = client.get_readme_candidate_files()
        urls = set()
        for readme in readmes:
            readme_content = readme.get("content")
            if readme_content:
                # Construct raw GitHub URL
                path = readme.get("path", "")
                owner = client.get_repository_owner()
                repo = client.get_repository_name()
                default_branch = client.get_repository().get("default_branch", "main")
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
                urls.add(raw_url)
        if urls:
            state.metadata_collector.collect("GitHub API", "https://codemeta.github.io/terms/readme", list(urls), 0.95)
        return state


class GitHubVersionControlSystemExtractor(GitHubBaseExtractor):
    """maSMP:versionControlSystem - hardcoded, since GitHub is a Git-only forge"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/versionControlSystem'}
    name = "github.version_control_system_extractor"

    def extract(self, context, state):
        state.metadata_collector.collect("Constant", "https://discovery.biothings.io/ns/maSMP/versionControlSystem", {
            "@type": "VersionControlSystem",
            "name": "Git",
            "url": "https://git-scm.com/",
        }, 1.0)
        return state


class GitHubArchivedAtExtractor(GitHubBaseExtractor):
    """schema:archivedAt"""

    extracts = {'https://schema.org/archivedAt'}
    name = "github.archived_at_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        zenodoUrls = set()
        for file in client.get_readme_candidate_files():
            readme_content = file.get("content")
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




class GitHubContributorsExtractor(GitHubBaseExtractor):
    """schema:contributor"""

    extracts = {'https://schema.org/contributor'}
    name = "github.contributors_extractor"

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
                        'name': contributor.get('login', ''),
                        'url': contributor.get('html_url', ''),
                        'contributions': contributor.get('contributions', 0)
                    }
                    contributors.append(person)
            if contributors:
                state.metadata_collector.collect("GitHub API", "https://schema.org/contributor", contributors, 0.95)
        except Exception:
            pass
        return state


class GitHubReleaseNotesExtractor(GitHubBaseExtractor):
    """schema:releaseNotes"""

    extracts = {'https://schema.org/releaseNotes', 'https://codemeta.github.io/terms/releaseNotes'}
    name = "github.release_notes_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        try:
            result = client.get_releases()
            if isinstance(result, list) and len(result) > 0:
                latest_release = result[0]
                body = latest_release.get("body")
                if body:
                    state.metadata_collector.collect("GitHub API", "https://schema.org/releaseNotes", body, 0.95)
                    state.metadata_collector.collect("GitHub API", 'https://codemeta.github.io/terms/releaseNotes', body, 0.95)
        except Exception:
            pass
        return state


class GitHubSoftwareVersionExtractor(GitHubBaseExtractor):
    """schema:softwareVersion"""

    extracts = {'https://schema.org/softwareVersion', 'https://schema.org/version'}
    name = "github.software_version_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        
        try:
            result = client.get_releases()
            if isinstance(result, list) and len(result) > 0:
                latest_release = result[0]
                tag_name = latest_release.get("tag_name")
                if tag_name:
                    state.metadata_collector.collect("GitHub API", "https://schema.org/softwareVersion", tag_name, 0.95)
                    state.metadata_collector.collect("GitHub API", "https://schema.org/version", tag_name, 0.95)
        except Exception:
            # Fallback to tags if no releases
            try:
                tags = client.get_tags()
                if isinstance(tags, list) and len(tags) > 0:
                    tag_name = tags[0].get("name")
                    if tag_name:
                        state.metadata_collector.collect("GitHub API", "https://schema.org/softwareVersion", tag_name, 0.85)
                        state.metadata_collector.collect("GitHub API", "https://schema.org/version", tag_name, 0.85)
            except Exception:
                pass
        
        # Check CFF for version
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'version' in citation:
                state.metadata_collector.collect("CFF File", "https://schema.org/softwareVersion", citation['version'], 0.85)
                state.metadata_collector.collect("CFF File", "https://schema.org/version", citation['version'], 0.85)
        return state


class GitHubHasSourceCodeExtractor(GitHubBaseExtractor):
    """maSMP:hasSourceCode"""

    extracts = {'https://codemeta.github.io/terms/hasSourceCode'}
    name = "github.has_source_code_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if 'html_url' in repo:
            has_source_code_url = repo['html_url']
            state.metadata_collector.collect("GitHub API", "https://codemeta.github.io/terms/hasSourceCode", has_source_code_url, 0.95)
        return state


class GitHubConditionsOfAccessExtractor(GitHubBaseExtractor):
    """schema:conditionOfAccess - SoftwareApplication slot, mirrors license"""

    extracts = {'https://schema.org/conditionOfAccess'}
    name = "github.conditions_of_access_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        license_info = result.get("license")
        if license_info and isinstance(license_info, dict):
            license_url = license_info.get("url") or license_info.get("spdx_id")
            if license_url:
                state.metadata_collector.collect("GitHub API", "https://schema.org/conditionOfAccess", license_url, 0.95)
        return state


class GitHubIsAccessibleForFreeExtractor(GitHubBaseExtractor):
    """maSMP:isAccessibleForFree - SoftwareApplication slot, based on repository privacy"""

    extracts = {'https://schema.org/isAccessibleForFree', 'https://schema.org/conditionOfAccess'}
    name = "github.is_accessible_for_free_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        private = repo.get("private")
        if private == False:
            state.metadata_collector.collect("GitHub API", "https://schema.org/isAccessibleForFree", True, 0.95)
            state.metadata_collector.collect("GitHub API", "https://schema.org/conditionOfAccess", 'Public', 0.95)
        elif private == True:
            state.metadata_collector.collect("GitHub API", "https://schema.org/isAccessibleForFree", False, 0.95)
            state.metadata_collector.collect("GitHub API", "https://schema.org/conditionOfAccess", 'Private', 0.95)
        return state


class GitHubDateExtractor(GitHubBaseExtractor):
    """extracts creation, modification, and publication dates for a GitHub repository,
    falling back to the latest release/tag date if no releases exist"""

    extracts = {'https://schema.org/dateCreated', 'https://schema.org/datePublished', 'https://schema.org/dateModified'}
    name = "github.date_extractor"

    def extract(self, context, state):
        def iso_dt_to_str(iso_dt):
            return str(datetime.datetime.fromisoformat(iso_dt.replace('Z', '+00:00')).date())
        
        client = self.get_client(context, state)
        repo = client.get_repository()
        
        if "created_at" in repo:
            state.metadata_collector.collect("GitHub API", 'https://schema.org/dateCreated', iso_dt_to_str(repo['created_at']), 0.95)
        if 'updated_at' in repo:
            state.metadata_collector.collect("GitHub API", 'https://schema.org/dateModified', iso_dt_to_str(repo['updated_at']), 0.95)
        
        try:
            releases = client.get_releases()
            if isinstance(releases, list) and len(releases) > 0:
                latest_release = releases[0]
                if 'published_at' in latest_release:
                    state.metadata_collector.collect("GitHub API", 'https://schema.org/datePublished', iso_dt_to_str(latest_release['published_at']), 0.85)
        except Exception:
            # Fallback to tags
            try:
                tags = client.get_tags()
                if isinstance(tags, list) and len(tags) > 0:
                    latest_tag = tags[0]
                    commit_date = latest_tag.get('commit', {}).get('date')
                    if commit_date:
                        state.metadata_collector.collect("GitHub API", 'https://schema.org/datePublished', iso_dt_to_str(commit_date), 0.6)
            except Exception:
                pass
        
        # Check CFF for release date
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'date-released' in citation:
                state.metadata_collector.collect('CFF File', 'https://schema.org/datePublished', citation['date-released'], 0.85)
        return state


class GitHubIssueTrackerExtractor(GitHubBaseExtractor):
    """extracts the issue tracker URL for a GitHub repository"""

    extracts = {'https://schema.org/issueTracker', 'https://codemeta.github.io/terms/issueTracker'}
    name = "github.issue_tracker_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('has_issues', False) and 'html_url' in repo:
            issue_tracker_url = f"{repo['html_url']}/issues"
            state.metadata_collector.collect("GitHub API", 'https://schema.org/issueTracker', issue_tracker_url, 0.95)
            state.metadata_collector.collect("GitHub API", 'https://codemeta.github.io/terms/issueTracker', issue_tracker_url, 0.95)
        return state


class GitHubChangelogExtractor(GitHubBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/changeLog'}
    name = "github.changelog_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        
        # Try to get changelog from releases
        try:
            if 'html_url' in repo:
                changelog_url = f"{repo['html_url']}/releases"
                state.metadata_collector.collect("Pattern", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.75)
        except Exception:
            pass
        
        # Look for CHANGELOG file
        try:
            files = client.list_contents()
            for file in files:
                if file.get('name', '').lower().startswith('changelog'):
                    download_url = file.get('download_url')
                    if download_url:
                        state.metadata_collector.collect("Changelog File", 'https://discovery.biothings.io/ns/maSMP/changeLog', download_url, 0.85)
        except Exception:
            pass
        return state


class GitHubSoftwareRequirementExtractor(GitHubBaseExtractor):
    """schema:softwareRequirements"""

    extracts = {'https://schema.org/softwareRequirements'}
    name = "github.software_requirements_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        try:
            files = client.list_contents()
            found = []
            for file in files:
                if file.get('name', '').lower() in dependency_files and file.get('download_url'):
                    found.append(file['download_url'])
            if len(found) > 0:
                state.metadata_collector.collect("GitHub API", 'https://schema.org/softwareRequirements', found, 0.95)
        except Exception:
            pass
        return state


class GitHubLicenseCopyrightHolderExtractor(GitHubBaseExtractor):
    """extracts the copyright holder and year from the license file"""

    name = "github.extract_copyright_year_and_holder"
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


class GitHubStorageRequirementExtractor(GitHubBaseExtractor):
    """extracts storage requirements from repository size"""

    name = "github.storage_requirement_extractor"
    extracts = {"https://schema.org/storageRequirements"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        size = repo.get('size')
        if size:
            size = float(size)
            units = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
            divider = 1
            for unit in units:
                if size / divider <= 1000:
                    break
                divider *= 1024
            sizeStr = f"{size / divider : .2f} {unit}"
            state.metadata_collector.collect('GitHub API', "https://schema.org/storageRequirements", sizeStr, 0.95)
        return state


class GitHubDownloadUrlExtractor(GitHubBaseExtractor):
    """extracts the download URL for the repository archive"""

    name = "github.download_url_extractor"
    extracts = {"https://schema.org/downloadUrl"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        default_branch = repo.get("default_branch", "main")
        if default_branch and not repo.get("empty", True):
            download_url = f"https://github.com/{client.get_repository_owner()}/{client.get_repository_name()}/archive/refs/heads/{default_branch}.zip"
            state.metadata_collector.collect("Pattern", "https://schema.org/downloadUrl", download_url, 0.95)
        return state


class GitHubStarsCountExtractor(GitHubBaseExtractor):
    """extracts the stars/watchers count for a GitHub repository"""

    name = "github.stars_count_extractor"
    extracts = {"https://schema.org/interactionCount"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        stargazers_count = repo.get('stargazers_count', 0)
        if stargazers_count > 0:
            state.metadata_collector.collect("GitHub API", "https://schema.org/interactionCount", f"StarAction:{stargazers_count}", 0.95)
        return state


class GitHubForksCountExtractor(GitHubBaseExtractor):
    """extracts the number of forks for a GitHub repository"""

    name = "github.forks_count_extractor"
    extracts = {"https://codemeta.github.io/terms/forks"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        forks_count = repo.get('forks_count', 0)
        if forks_count >= 0:
            state.metadata_collector.collect("GitHub API", "https://codemeta.github.io/terms/forks", forks_count, 0.95)
        return state