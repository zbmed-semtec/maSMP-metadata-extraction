"""Codeberg extractor plugins for populating schema.org / codemeta / maSMP
metadata fields from a repository's Codeberg API data, CITATION.cff files,
README files, and license files."""

from app.layer_3.plugins.codeberg.codeberg_client import CodebergClient
from app.layer_3.plugins.codeberg.codeberg_base_extractor import CodebergBaseExtractor
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher
from app.layer_3.plugins.codeberg.utils import match_license_text
from app.layer_3.plugins.extract_wayback_archived_url_step import WaybackClient

class CodebergNameExtractor(CodebergBaseExtractor):
    """schema:name"""

    extracts = {'https://schema.org/name'}
    platforms = {'codeberg.org'}
    name = "codeberg.name_extractor"

    def extract(self, context, state):
        # getting the name from the API
        result = self.get_client(context, state).get_repository()
        if result.get("name"):
            state.metadata_collector.collect("Codeberg API", "https://schema.org/name", result['name'], 0.95)
        # getting the name from the CFF
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'title' in cff:
                state.metadata_collector.collect("CFF File", "https://schema.org/name", cff['title'], 0.85)
        return state

class CodebergDescriptionExtractor(CodebergBaseExtractor):
    """schema:description"""

    extracts = {'https://schema.org/description'}
    platforms = {'codeberg.org'}
    name = "codeberg.description_extractor"

    def extract(self, context, state):
        # getting the description from the Codeberg API
        result = self.get_client(context, state).get_repository()
        if result.get("description"):
            state.metadata_collector.collect("Codeberg API", "https://schema.org/description", result['description'], 0.95)
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

class CodebergUrlExtractor(CodebergBaseExtractor):
    """schema:url"""

    extracts = {'https://schema.org/url'}
    platforms = {'codeberg.org'}
    name = "codeberg.url_extractor"

    def extract(self, context, state):
        # getting the URL from the Codeberg API
        result = self.get_client(context, state).get_repository()
        if result.get("html_url"):
            state.metadata_collector.collect("Codeberg API", "https://schema.org/url", result['html_url'], 0.95)
        # getting the URL from CITATION.cff
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'url' in cff:
                state.metadata_collector.collect("CFF File", 'https://schema.org/url', cff['url'], 0.85)
        return state

class CodebergCodeRepositoryExtractor(CodebergBaseExtractor):
    """schema:codeRepository"""

    extracts = {'https://schema.org/codeRepository'}
    platforms = {'codeberg.org'}
    name = "codeberg.code_repository_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        clone_url = result.get("clone_url") or result.get("html_url")
        if clone_url:
            state.metadata_collector.collect("Codeberg API", "https://schema.org/codeRepository", clone_url, 0.95)
        return state

class CodebergProgrammingLanguageExtractor(CodebergBaseExtractor):
    """schema:programmingLanguage"""

    extracts = {'https://schema.org/programmingLanguage'}
    platforms = {'codeberg.org'}
    name = "codeberg.programming_language_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_languages()
        if isinstance(result, dict) and result:
            languages = list(result.keys())
            state.metadata_collector.collect("Codeberg API", "https://schema.org/programmingLanguage", languages, 0.95)
        return state

class CodebergAuthorExtractor(CodebergBaseExtractor):
    """schema:author - multivalued, so we combine owner + contributors"""

    extracts = {'https://schema.org/author'}
    platforms = {'codeberg.org'}
    name = "codeberg.author_extractor"

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
        return state

class CodebergLicenseExtractor(CodebergBaseExtractor):
    """schema:license"""

    extracts = {'https://schema.org/license'}
    platforms = {'codeberg.org'}
    name = "codeberg.license_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        license_candidates = client.get_license_candidate_files()
        for license_candidate in license_candidates:
            text = license_candidate.get("content")
            result = match_license_text(text)
            spdx_id = result["detected_license_expression_spdx"]
            conf    = result["percentage_of_license_text"] * 0.95 / 100.0
            license_object = {
                '@type': 'CreativeWork',
                '@context': 'https://schema.org',
                'name': spdx_id,
                'url' : f'https://spdx.org/licenses/{spdx_id}.html'
            }
            state.metadata_collector.collect("License File", 'https://schema.org/license', license_object, conf)
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'license' in citation:
                pass # TODO: Implement
            if 'license-url' in citation:
                pass # TODO: Implement
        return state

class CodebergIdentifierExtractor(CodebergBaseExtractor):
    """schema:identifier - use repository numeric id"""

    extracts = {'https://schema.org/identifier'}
    platforms = {'codeberg.org'}
    name = "codeberg.identifier_extractor"

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

class CodebergCitationExtractor(CodebergBaseExtractor):
    """schema:citation - from CFF preferred-citation"""

    extracts = {'https://schema.org/citation'}
    platforms = {'codeberg.org'}
    name = "codeberg.citation_extractor"

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
            else:
                # If no preferred-citation, we can still try to extract a DOI from the CFF file
                doi_value = cff.get("doi")
                if doi_value:
                    doi_url = f"https://doi.org/{str(doi_value)}"
                    citation_entry = {"@type": "Article", "@id": doi_url}
                    state.metadata_collector.collect("CFF File", "https://schema.org/citation", citation_entry, 0.85)
        return state

class CodebergKeywordsExtractor(CodebergBaseExtractor):
    """schema:keywords"""

    extracts = {'https://schema.org/keywords'}
    platforms = {'codeberg.org'}
    name = "codeberg.keywords_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        if "topics" in result and result["topics"]:
            state.metadata_collector.collect("Codeberg API", "https://schema.org/keywords", result['topics'], 0.95)
        client = self.get_client(context, state)
        citations = client.get_parsed_citations()
        keywords = []
        for cff in citations:
            keywords.extend(cff.get('keywords', []))
        if len(keywords) > 0:
            state.metadata_collector.collect("CFF File", "https://schema.org/keywords", keywords, 0.85)
        return state

class CodebergReadmeExtractor(CodebergBaseExtractor):
    """codemeta:readme"""

    extracts = {'https://codemeta.github.io/terms/readme'}
    platforms = {'codeberg.org'}
    name = "codeberg.readme_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        readmes = client.get_readme_candidate_files()
        urls = set()
        for readme in readmes:
            readme_content = readme.get("content")
            if readme_content:
                urls.add(readme.get("html_url"))
        if urls:
            state.metadata_collector.collect("Codeberg API", "https://codemeta.github.io/terms/readme", list(urls), 0.95)
        return state

class CodebergVersionControlSystemExtractor(CodebergBaseExtractor):
    """maSMP:versionControlSystem - hardcoded, since Codeberg is a Git-only forge"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/versionControlSystem'}
    platforms = {'codeberg.org'}
    name = "codeberg.version_control_system_extractor"

    def extract(self, context, state):
        state.metadata_collector.collect("Constant", "https://discovery.biothings.io/ns/maSMP/versionControlSystem", {
            "@type": "VersionControlSystem",
            "name": "Git",
            "url": "https://git-scm.com/",
        }, 1.0)
        return state

class CodebergArchivedAtExtractor(CodebergBaseExtractor):
    """schema:archivedAt - only meaningful if the repo is archived"""

    extracts = {'https://schema.org/archivedAt'}
    platforms = {'codeberg.org'}
    name = "codeberg.archived_at_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        zenodoUrls = set()
        for file in client.get_readme_candidate_files():
            readme_content = file["content"]
            candidates = URLPatternMatcher.check_zenodo_badge(readme_content)
            for url in candidates:
                zenodoUrls.add(url)
        if zenodoUrls:
            state.metadata_collector.collect("README", "https://schema.org/archivedAt", list(zenodoUrls), 0.6)
        waybackUrl = WaybackClient.check_archive_url(context.repo_url)
        if waybackUrl:
            state.metadata_collector.collect("Wayback API", "https://schema.org/archivedAt", [waybackUrl], 0.95)
        return state

class CodebergContributorsExtractor(CodebergBaseExtractor):
    """Not in schema explicitly, but kept for downstream use / possible mapping to author.
       Not registered against a schema slot at this time."""

    extracts = {'https://schema.org/contributor'}
    platforms = {'codeberg.org'}
    name = "codeberg.contributors_extractor"

    def extract(self, context, state):
        try:
            result = self.get_client(context, state).get_contributors()
            contributors = [{'name': contributor['name'], 'email':email, '@type': 'Person', "@context": 'https://schema.org'} for email, contributor in result.items() if email.lower() != 'total']
            state.metadata_collector.collect("Codeberg API", "https://schema.org/contributor", contributors, 0.95)
        except:
            pass
        return state

class CodebergReleaseNotesExtractor(CodebergBaseExtractor):
    """schema:releaseNotes - SoftwareApplication slot, from latest release body"""

    extracts = {'https://schema.org/releaseNotes'}
    platforms = {'codeberg.org'}
    name = "codeberg.release_notes_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_releases()
        if isinstance(result, list) and len(result) > 0:
            body = result[0].get("body")
            if body:
                state.metadata_collector.collect("Codeberg API", "https://schema.org/releaseNotes", body, 0.95)
        return state

class CodebergSoftwareVersionExtractor(CodebergBaseExtractor):
    """schema:softwareVersion - SoftwareApplication slot, mirrors version"""

    extracts = {'https://schema.org/softwareVersion', 'https://schema.org/version'}
    platforms = {'codeberg.org'}
    name = "codeberg.software_version_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_tags()
        if isinstance(result, list) and len(result) > 0:
            tag_name = result[0].get("name")
            if tag_name:
                state.metadata_collector.collect("Codeberg API", "https://schema.org/softwareVersion", tag_name, 0.85)
                state.metadata_collector.collect("Codeberg API", "https://schema.org/version", tag_name, 0.85)
        client = self.get_client(context, state)
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'version' in citation:
                state.metadata_collector.collect("CFF File", "https://schema.org/softwareVersion", citation['version'], 0.85)
                state.metadata_collector.collect("CFF File", "https://schema.org/version", citation['version'], 0.85)
        return state

class CodebergHasSourceCodeExtractor(CodebergBaseExtractor):
    """maSMP:hasSourceCode - SoftwareApplication slot, mirrors codeRepository"""

    extracts = {'https://codemeta.github.io/terms/hasSourceCode'}
    platforms = {'codeberg.org'}
    name = "codeberg.has_source_code_extractor"

    def extract(self, context, state):
        c = self.get_client(context, state)
        hasSourceCodeUrl = f"https://codeberg.org/{c.get_repository_owner()}/{c.get_repository_name()}/#id" 
        if hasSourceCodeUrl:
            state.metadata_collector.collect("Pattern", "https://codemeta.github.io/terms/hasSourceCode", hasSourceCodeUrl, 0.75)
        return state

class CodebergConditionsOfAccessExtractor(CodebergBaseExtractor):
    """schema:conditionsOfAccess - SoftwareApplication slot, mirrors license"""

    extracts = {'https://schema.org/conditionOfAccess'}
    platforms = {'codeberg.org'}
    name = "codeberg.conditions_of_access_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        license_info = result.get("license")
        if license_info and isinstance(license_info, dict):
            license_url = license_info.get("url") or license_info.get("key")
            if license_url:
                state.metadata_collector.collect("Codeberg API", "https://schema.org/conditionOfAccess", license_url, 0.95)
        return state

class CodebergIsAccessibleForFreeExtractor(CodebergBaseExtractor):
    """maSMP:isAccessibleForFree - SoftwareApplication slot, hardcoded to True"""

    extracts = {'https://schema.org/isAccessibleForFree', 'https://schema.org/conditionOfAccess'}
    platforms = {'codeberg.org'}
    name = "codeberg.is_accessible_for_free_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        private = repo.get("private")
        if private == False:
            state.metadata_collector.collect("Codeberg API", "https://schema.org/isAccessibleForFree", True, 0.95)
            state.metadata_collector.collect("Codeberg API", "https://schema.org/conditionOfAccess", 'Public', 0.95)
        elif private == True:
            state.metadata_collector.collect("Codeberg API", "https://schema.org/isAccessibleForFree", False, 0.95)
            state.metadata_collector.collect("Codeberg API", "https://schema.org/conditionOfAccess", 'Private', 0.95)
        return state

class CodebergDateExtractor(CodebergBaseExtractor):
    """extracts creation, modification, and publication dates for a Codeberg repository,
    falling back to the latest tag's commit date if no releases exist"""

    extracts = {'https://schema.org/dateCreated', 'https://schema.org/datePublished', 'https://schema.org/dateModified'}
    platforms = {'codeberg.org'}
    name = "codeberg.date_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if "created_at" in repo:
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/dateCreated', repo['created_at'], 0.95)
        if 'updated_at' in repo:
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/dateModified', repo['updated_at'], 0.95)
        if repo.get("has_releases", False):
            releases = client.get_releases()
            if len(releases) > 0:
                latest = releases[0]
                if 'published_at' in latest:
                    state.metadata_collector.collect("Codeberg API", 'https://schema.org/datePublished', latest['published_at'], 0.85)
        else: # if there are no releases, assume the latest tag acts as a release
            tags = client.get_tags()
            if len(tags) > 0:
                latest = tags[0]
                tag_time = latest.get('commit', {}).get('created')
                if tag_time:
                    state.metadata_collector.collect("Codeberg API", 'https://schema.org/datePublished', tag_time, 0.6)
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'date-released' in citation:
                state.metadata_collector.collect('CFF File', 'https://schema.org/datePublished', citation['date-released'], 0.85)
        return state

class CodebergIssueTrackerExtractor(CodebergBaseExtractor):
    """extracts the issue tracker URL for a Codeberg repository"""

    extracts = {'https://schema.org/issueTracker'}
    platforms = {'codeberg.org'}
    name = "codeberg.issue_tracker_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('has_issues', False) and 'html_url' in repo:
            issue_tracker_url = f"{repo['html_url']}/issues"
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/issueTracker', issue_tracker_url, 0.95)
        return state

class CodebergChangelogExtractor(CodebergBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/changeLog'}
    platforms = {'codeberg.org'}
    name = "codeberg.changelog_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('has_releases', False):
            if 'html_url' in repo:
                changelog_url = f"{repo['html_url']}/releases"
                state.metadata_collector.collect("Pattern", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.75)
        files = client.list_contents()
        for file in files:
            if file.get('name', '').lower().startswith('changelog'):
                changelog_url = file.get('download_url')
                if changelog_url:
                    state.metadata_collector.collect("Changelog File", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.6)
        return state