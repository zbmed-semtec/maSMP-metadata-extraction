"""Codeberg extractor plugins for populating schema.org / codemeta / maSMP
metadata fields from a repository's Codeberg API data, CITATION.cff files,
README files, and license files."""

import re

from app.layer_3.plugins.codeberg.codeberg_client import CodebergClient
from app.layer_3.plugins.codeberg.codeberg_base_extractor import CodebergBaseExtractor
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher
from app.layer_3.plugins.codeberg.utils import match_license_text, dependency_files
from app.layer_3.plugins.extract_wayback_archived_url_step import WaybackClient
import datetime

class CodebergNameExtractor(CodebergBaseExtractor):
    """schema:name"""

    extracts = {'https://schema.org/name'}
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

    extracts = {'https://schema.org/codeRepository', 'https://codemeta.github.io/terms/codeRepository'}
    name = "codeberg.code_repository_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        clone_url = result.get("clone_url") or result.get("html_url")
        if clone_url:
            state.metadata_collector.collect("Codeberg API", "https://schema.org/codeRepository", clone_url, 0.95)
            state.metadata_collector.collect("Codeberg API", 'https://codemeta.github.io/terms/codeRepository', clone_url, 0.95)
        return state

class CodebergProgrammingLanguageExtractor(CodebergBaseExtractor):
    """schema:programmingLanguage"""

    extracts = {'https://schema.org/programmingLanguage'}
    name = "codeberg.programming_language_extractor"

    def extract(self, context, state):
        result = self.get_client(context, state).get_languages()
        if isinstance(result, dict) and result:
            languages = list(result.keys())
            state.metadata_collector.collect("Codeberg API", "https://schema.org/programmingLanguage", languages, 0.95)
        return state

class CodebergAuthorExtractor(CodebergBaseExtractor):
    """schema:author"""

    extracts = {'https://schema.org/author'}
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
    """schema:identifier"""

    extracts = {'https://schema.org/identifier'}
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

class CodebergCitationExtractor(CodebergBaseExtractor):
    """schema:citation"""

    extracts = {'https://schema.org/citation', "https://schema.org/alternateName", "https://codemeta.github.io/terms/referencePublication"}
    name = "codeberg.citation_extractor"

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
                    citation_entry = {"@type": "Software", "@id": doi_url}
                    state.metadata_collector.collect("CFF File", "https://schema.org/citation", citation_entry, 0.85)

            # Extract 'references' field from CFF (list of related works/citations)
            references_field = cff.get("references") or []
            for ref in references_field:
                if not isinstance(ref, dict):
                    continue
                ref_citation_entry = self._build_citation_entry(ref)
                state.metadata_collector.collect("CFF File", "https://schema.org/citation", ref_citation_entry, 0.85)

        return state

class CodebergKeywordsExtractor(CodebergBaseExtractor):
    """schema:keywords"""

    extracts = {'https://schema.org/keywords'}
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
    name = "codeberg.version_control_system_extractor"

    def extract(self, context, state):
        state.metadata_collector.collect("Constant", "https://discovery.biothings.io/ns/maSMP/versionControlSystem", {
            "@type": "VersionControlSystem",
            "name": "Git",
            "url": "https://git-scm.com/",
        }, 1.0)
        return state

class CodebergArchivedAtExtractor(CodebergBaseExtractor):
    """schema:archivedAt"""

    extracts = {'https://schema.org/archivedAt'}
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

    extracts = {'https://schema.org/contributor'}
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
    """schema:releaseNotes"""

    extracts = {'https://schema.org/releaseNotes','https://codemeta.github.io/terms/releaseNotes'}
    name = "codeberg.release_notes_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        has_release = repo.get("has_release", False)
        if has_release:
            result = self.get_client(context, state).get_releases()
            if isinstance(result, list) and len(result) > 0:
                body = result[0].get("body")
                if body:
                    state.metadata_collector.collect("Codeberg API", "https://schema.org/releaseNotes", body, 0.95)
                    state.metadata_collector.collect("Codeberg API", 'https://codemeta.github.io/terms/releaseNotes', body, 0.95)
        return state

class CodebergSoftwareVersionExtractor(CodebergBaseExtractor):
    """schema:softwareVersion"""

    extracts = {'https://schema.org/softwareVersion', 'https://schema.org/version'}
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
    """maSMP:hasSourceCode"""

    extracts = {'https://codemeta.github.io/terms/hasSourceCode'}
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
    name = "codeberg.date_extractor"

    def extract(self, context, state):
        def iso_dt_to_str(iso_dt):
            return str(datetime.datetime.fromisoformat(iso_dt).date())
        client = self.get_client(context, state)
        repo = client.get_repository()
        if "created_at" in repo:
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/dateCreated', iso_dt_to_str(repo['created_at']), 0.95)
        if 'updated_at' in repo:
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/dateModified', iso_dt_to_str(repo['updated_at']), 0.95)
        if repo.get("has_releases", False):
            releases = client.get_releases()
            if len(releases) > 0:
                latest = releases[0]
                if 'published_at' in latest:
                    state.metadata_collector.collect("Codeberg API", 'https://schema.org/datePublished', iso_dt_to_str(latest['published_at']), 0.85)
        else: # if there are no releases, assume the latest tag acts as a release
            tags = client.get_tags()
            if len(tags) > 0:
                latest = tags[0]
                tag_time = latest.get('commit', {}).get('created')
                if tag_time:
                    state.metadata_collector.collect("Codeberg API", 'https://schema.org/datePublished', iso_dt_to_str(tag_time), 0.6)
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'date-released' in citation:
                state.metadata_collector.collect('CFF File', 'https://schema.org/datePublished', citation['date-released'], 0.85)
        return state

class CodebergIssueTrackerExtractor(CodebergBaseExtractor):
    """extracts the issue tracker URL for a Codeberg repository"""

    extracts = {'https://schema.org/issueTracker','https://codemeta.github.io/terms/issueTracker'}
    name = "codeberg.issue_tracker_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('has_issues', False) and 'html_url' in repo:
            issue_tracker_url = f"{repo['html_url']}/issues"
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/issueTracker', issue_tracker_url, 0.95)
            state.metadata_collector.collect("Codeberg API", 'https://codemeta.github.io/terms/issueTracker', issue_tracker_url, 0.95)
        return state

class CodebergChangelogExtractor(CodebergBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/changeLog'}
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
                    state.metadata_collector.collect("Changelog File", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.85)
        return state

class CodebergSoftwareRequirementExtractor(CodebergBaseExtractor):
    
    extracts = {'https://schema.org/softwareRequirements'}
    name = "codeberg.software_requirements_extractor"

    def extract(self, context, state):
        client = self.get_client(context, state)
        files = client.list_contents()
        found = []
        for file in files:
            if file.get('name', '').lower() in dependency_files and file.get('download_url'):
                found.append(file['download_url'])
        if len(found) > 0:
            state.metadata_collector.collect("Codeberg API", 'https://schema.org/softwareRequirements', found, 0.95)
        return state

class CodebergLicenseCopyrightHolderExtractor(CodebergBaseExtractor):
    """extracts the copyright holder and year from the license file"""

    name = "codeberg.extract_copyright_year_and_holder"
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
        licenses = client.get_license_candidate_files()
        for license in licenses:
            year, holder = extract_copyright_holder(license.get("content", ""))
            if holder:
                state.metadata_collector.collect("License File", "https://schema.org/copyrightHolder", holder.strip(), 0.85)
            if year:
                try:
                    year = int(year)
                    state.metadata_collector.collect("License File", "https://schema.org/copyrightYear", year, 0.85)
                except:
                    pass
                
        return state 
    
class CodebergStorageReqExtractor(CodebergBaseExtractor):
    """extracts the copyright holder and year from the license file"""

    name = "codeberg.storage_requirement_extractor"
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
            state.metadata_collector.collect('Codeberg API', "https://schema.org/storageRequirements", sizeStr, 0.95)
        return state

class CodebergDownloadUrlExtractor(CodebergBaseExtractor):
    """extracts the copyright holder and year from the license file"""

    name = "codeberg.codeberg_download_url_extractor"
    extracts = {"https://schema.org/downloadUrl"}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        default_branch = repo.get("default_branch")
        is_empty = repo.get("empty", True)
        if default_branch and not is_empty:
            download_url = f"https://codeberg.org/{client.get_repository_owner()}/{client.get_repository_name()}/archive/{default_branch}.zip"
            state.metadata_collector.collect("Pattern", "https://schema.org/downloadUrl", download_url, 0.95)
        return state