import re
import datetime
from app.layer_3.plugins.shared.git_platform_base_extractor import GitPlatformBaseExtractor
from app.layer_3.plugins.url_pattern_matcher_plugin import URLPatternMatcher
from app.layer_3.plugins.codeberg.utils import match_license_text, dependency_files
from app.layer_3.plugins.shared.wayback_client import WaybackClient
from app.layer_3.plugins.shared.software_heritage_client import SoftwareHeritageClient
from app.layer_3.plugins.shared.open_alex_client import OpenAlexClient

class GitPlatformNameExtractor(GitPlatformBaseExtractor):
    """schema:name"""

    extracts = {'https://schema.org/name'}

    def extract(self, context, state):
        
        # getting the name from the API
        result = self.get_client(context, state).get_repository()
        if result.get("name"):
            state.metadata_collector.collect("Platform API", "https://schema.org/name", result['name'], 0.95)
        
        # getting the name from the CFF
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'title' in cff:
                state.metadata_collector.collect("CFF File", "https://schema.org/name", cff['title'], 0.85)
        return state

class GitPlatformDescriptionExtractor(GitPlatformBaseExtractor):
    """schema:description"""

    extracts = {'https://schema.org/description'}

    def extract(self, context, state):
        # getting the description from the GitLab API
        result = self.get_client(context, state).get_repository()
        if result.get("description"):
            state.metadata_collector.collect("Platform API", "https://schema.org/description", result['description'], 0.95)

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

class GitPlatformUrlExtractor(GitPlatformBaseExtractor):
    """schema:url"""

    extracts = {'https://schema.org/url'}

    def extract(self, context, state):
        # getting the URL from the Platform API
        result = self.get_client(context, state).get_repository()
        if result.get("html_url"):
            state.metadata_collector.collect("Platform API", "https://schema.org/url", result['html_url'], 0.95)
        # getting the URL from CITATION.cff
        client = self.get_client(context, state)
        cffs = client.get_parsed_citations()
        for cff in cffs:
            if 'url' in cff:
                state.metadata_collector.collect("CFF File", 'https://schema.org/url', cff['url'], 0.85)
        return state

class GitPlatformCodeRepositoryExtractor(GitPlatformBaseExtractor):
    """schema:codeRepository"""

    extracts = {'https://schema.org/codeRepository', 'https://codemeta.github.io/terms/codeRepository'}

    def extract(self, context, state):
        clone_url = self.get_client(context, state).get_clone_url()
        if clone_url:
            state.metadata_collector.collect("Platform API", "https://schema.org/codeRepository", clone_url, 0.95)
            state.metadata_collector.collect("Platform API", 'https://codemeta.github.io/terms/codeRepository', clone_url, 0.95)
        return state

class GitPlatformProgrammingLanguageExtractor(GitPlatformBaseExtractor):
    """schema:programmingLanguage"""

    extracts = {'https://schema.org/programmingLanguage'}

    def extract(self, context, state):
        result = self.get_client(context, state).get_languages()
        if isinstance(result, dict) and result:
            languages = list(result.keys())
            state.metadata_collector.collect("Platform API", "https://schema.org/programmingLanguage", languages, 0.95)
        return state

class GitPlatformAuthorExtractor(GitPlatformBaseExtractor):
    """schema:author"""

    extracts = {'https://schema.org/author'}

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

class GitPlatformLicenseExtractor(GitPlatformBaseExtractor):
    """schema:license"""

    extracts = {'https://schema.org/license'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        license_candidates = client.get_license_candidate_files()
        for license_candidate in license_candidates:
            text = license_candidate.get_content()
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
                license_value = citation.get('license')
                if license_value:
                    result = match_license_text(license_value)
                    spdx_id = result["detected_license_expression_spdx"]
                    conf    = result["percentage_of_license_text"] * 0.95 / 100.0
                    if spdx_id:
                        license_object = {
                            '@type': 'CreativeWork',
                            '@context': 'https://schema.org',
                            'name': spdx_id,
                            'url' : f'https://spdx.org/licenses/{spdx_id}.html'
                        }
                    else:
                        # Fall back to using the raw citation value as the name
                        # if no SPDX match could be determined.
                        license_object = {
                            '@type': 'CreativeWork',
                            '@context': 'https://schema.org',
                            'name': license_value
                        }
                    state.metadata_collector.collect(
                        "CITATION.cff", 'https://schema.org/license', license_object, conf
                    )
            if 'license-url' in citation:
                license_url = citation.get('license-url')
                if license_url:
                    license_object = {
                        '@type': 'CreativeWork',
                        '@context': 'https://schema.org',
                        'url': license_url
                    }
                    # license-url is an explicit, author-provided value, so we treat
                    # it with high confidence, similar to other direct metadata fields.
                    conf = 0.9
                    state.metadata_collector.collect(
                        "CITATION.cff", 'https://schema.org/license', license_object, conf
                    )
        return state

class GitPlatformIdentifierExtractor(GitPlatformBaseExtractor):
    """schema:identifier"""

    extracts = {'https://schema.org/identifier'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        
        # from CFF
        identifiers = list(client.get_dois_from_parsed_citaitons())
        if len(identifiers) > 0:
            state.metadata_collector.collect("CFF File", "https://schema.org/identifier", identifiers, 0.85)

        # from README
        identifiers = list(client.get_dois_from_readmes())
        if len(identifiers) > 0:
            state.metadata_collector.collect("README", "https://schema.org/identifier", identifiers, 0.6)
        return state

class GitPlatformCitationExtractor(GitPlatformBaseExtractor):
    """schema:citation"""

    extracts = {'https://schema.org/citation', "https://schema.org/alternateName", "https://codemeta.github.io/terms/referencePublication"}

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

class GitPlatformKeywordsExtractor(GitPlatformBaseExtractor):
    """schema:keywords"""

    extracts = {'https://schema.org/keywords'}

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        if "topics" in result and result["topics"]:
            state.metadata_collector.collect("Platform API", "https://schema.org/keywords", result['topics'], 0.95)
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

class GitPlatformReadmeExtractor(GitPlatformBaseExtractor):
    """codemeta:readme"""

    extracts = {'https://codemeta.github.io/terms/readme'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        readmes = client.get_readme_candidate_files()
        urls = set()
        for readme in readmes:
            readme_content = readme.get_content()
            if readme_content:
                urls.add(readme.get_html_url(client))
        if urls:
            state.metadata_collector.collect("Platform API", "https://codemeta.github.io/terms/readme", list(urls), 0.95)
        return state

class GitPlatformVersionControlSystemExtractor(GitPlatformBaseExtractor):
    """maSMP:versionControlSystem - hardcoded, since Platform is a Git-only forge"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/versionControlSystem'}

    def extract(self, context, state):
        state.metadata_collector.collect("Constant", "https://discovery.biothings.io/ns/maSMP/versionControlSystem", {
            "@type": "VersionControlSystem",
            "name": "Git",
            "url": "https://git-scm.com/",
        }, 1.0)
        return state

class GitPlatformArchivedAtExtractor(GitPlatformBaseExtractor):
    """schema:archivedAt"""

    extracts = {'https://schema.org/archivedAt'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        zenodoUrls = set()
        for file in client.get_readme_candidate_files():
            readme_content = file.get_content()
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
            state.metadata_collector.collect("SoftwareHeritage API", "https://schema.org/archivedAt", [softwareHeritageUrl], 0.95)
        return state

class GitPlatformContributorsExtractor(GitPlatformBaseExtractor):

    extracts = {'https://schema.org/contributor'}

    def extract(self, context, state):
        try:
            result = self.get_client(context, state).get_contributors()
            contributors = [{'name': contributor['name'], 'email':email, '@type': 'Person', "@context": 'https://schema.org'} for email, contributor in result.items() if email.lower() != 'total']
            state.metadata_collector.collect("Platform API", "https://schema.org/contributor", contributors, 0.95)
        except:
            pass
        return state

class GitPlatformReleaseNotesExtractor(GitPlatformBaseExtractor):
    """schema:releaseNotes"""

    extracts = {'https://schema.org/releaseNotes','https://codemeta.github.io/terms/releaseNotes'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        has_release = repo.get("has_release", False)
        if has_release:
            result = self.get_client(context, state).get_releases()
            if isinstance(result, list) and len(result) > 0:
                body = result[0].get("body")
                if body:
                    state.metadata_collector.collect("Platform API", "https://schema.org/releaseNotes", body, 0.95)
                    state.metadata_collector.collect("Platform API", 'https://codemeta.github.io/terms/releaseNotes', body, 0.95)
        return state

class GitPlatformSoftwareVersionExtractor(GitPlatformBaseExtractor):
    """schema:softwareVersion"""

    extracts = {'https://schema.org/softwareVersion', 'https://schema.org/version'}

    def extract(self, context, state):
        result = self.get_client(context, state).get_tags()
        if isinstance(result, list) and len(result) > 0:
            tag_name = result[0].get("name")
            if tag_name:
                state.metadata_collector.collect("Platform API", "https://schema.org/softwareVersion", tag_name, 0.85)
                state.metadata_collector.collect("Platform API", "https://schema.org/version", tag_name, 0.85)
        client = self.get_client(context, state)
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'version' in citation:
                state.metadata_collector.collect("CFF File", "https://schema.org/softwareVersion", citation['version'], 0.85)
                state.metadata_collector.collect("CFF File", "https://schema.org/version", citation['version'], 0.85)
        return state

class GitPlatformHasSourceCodeExtractor(GitPlatformBaseExtractor):
    """maSMP:hasSourceCode"""

    extracts = {'https://codemeta.github.io/terms/hasSourceCode'}

    def extract(self, context, state):
        c = self.get_client(context, state)
        hasSourceCodeUrl = f"https://Platform.org/{c.get_repository_owner()}/{c.get_repository_name()}/#id" 
        if hasSourceCodeUrl:
            state.metadata_collector.collect("Pattern", "https://codemeta.github.io/terms/hasSourceCode", hasSourceCodeUrl, 0.75)
        return state

class GitPlatformConditionsOfAccessExtractor(GitPlatformBaseExtractor):
    """schema:conditionsOfAccess - SoftwareApplication slot, mirrors license"""

    extracts = {'https://schema.org/conditionOfAccess'}

    def extract(self, context, state):
        result = self.get_client(context, state).get_repository()
        license_info = result.get("license")
        if license_info and isinstance(license_info, dict):
            license_url = license_info.get("url") or license_info.get("key")
            if license_url:
                state.metadata_collector.collect("Platform API", "https://schema.org/conditionOfAccess", license_url, 0.95)
        return state

class GitPlatformIsAccessibleForFreeExtractor(GitPlatformBaseExtractor):
    """maSMP:isAccessibleForFree - SoftwareApplication slot, hardcoded to True"""

    extracts = {'https://schema.org/isAccessibleForFree', 'https://schema.org/conditionOfAccess'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        private = repo.get("private")
        if private == False:
            state.metadata_collector.collect("Platform API", "https://schema.org/isAccessibleForFree", True, 0.95)
            state.metadata_collector.collect("Platform API", "https://schema.org/conditionOfAccess", 'Public', 0.95)
        elif private == True:
            state.metadata_collector.collect("Platform API", "https://schema.org/isAccessibleForFree", False, 0.95)
            state.metadata_collector.collect("Platform API", "https://schema.org/conditionOfAccess", 'Private', 0.95)
        return state

class GitPlatformDateExtractor(GitPlatformBaseExtractor):
    """extracts creation, modification, and publication dates for a Platform repository,
    falling back to the latest tag's commit date if no releases exist"""

    extracts = {'https://schema.org/dateCreated', 'https://schema.org/datePublished', 'https://schema.org/dateModified'}

    def extract(self, context, state):
        def iso_dt_to_str(iso_dt):
            return str(datetime.datetime.fromisoformat(str(iso_dt)).date())
        client = self.get_client(context, state)
        repo = client.get_repository()
        if "created_at" in repo:
            state.metadata_collector.collect("Platform API", 'https://schema.org/dateCreated', iso_dt_to_str(repo['created_at']), 0.95)
        if 'updated_at' in repo:
            state.metadata_collector.collect("Platform API", 'https://schema.org/dateModified', iso_dt_to_str(repo['updated_at']), 0.95)
        if repo.get("has_releases", False):
            releases = client.get_releases()
            if len(releases) > 0:
                latest = releases[0]
                if 'published_at' in latest:
                    state.metadata_collector.collect("Platform API", 'https://schema.org/datePublished', iso_dt_to_str(latest['published_at']), 0.85)
        else: # if there are no releases, assume the latest tag acts as a release
            tags = client.get_tags()
            if len(tags) > 0:
                latest = tags[0]
                tag_time = latest.get('commit', {}).get('created')
                if tag_time:
                    state.metadata_collector.collect("Platform API", 'https://schema.org/datePublished', iso_dt_to_str(tag_time), 0.6)
        citations = client.get_parsed_citations()
        for citation in citations:
            if 'date-released' in citation:
                state.metadata_collector.collect('CFF File', 'https://schema.org/datePublished', iso_dt_to_str(citation['date-released']), 0.85)
        return state

class GitPlatformIssueTrackerExtractor(GitPlatformBaseExtractor):
    """extracts the issue tracker URL for a Platform repository"""

    extracts = {'https://schema.org/issueTracker','https://codemeta.github.io/terms/issueTracker'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('has_issues', False) and 'html_url' in repo:
            issue_tracker_url = f"{repo['html_url']}/issues"
            state.metadata_collector.collect("Platform API", 'https://schema.org/issueTracker', issue_tracker_url, 0.95)
            state.metadata_collector.collect("Platform API", 'https://codemeta.github.io/terms/issueTracker', issue_tracker_url, 0.95)
        return state

class GitPlatformChangelogExtractor(GitPlatformBaseExtractor):
    """maSMP:changeLog - derived from the releases page and/or a CHANGELOG file in the repo root"""

    extracts = {'https://discovery.biothings.io/ns/maSMP/changeLog'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        repo = client.get_repository()
        if repo.get('has_releases', False):
            if 'html_url' in repo:
                changelog_url = f"{repo['html_url']}/releases"
                state.metadata_collector.collect("Pattern", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.75)
        files = client.get_changelog_candidate_files()
        for file in files:
            if (file.get_content() or "").lower().startswith('changelog'):
                changelog_url = file.get('download_url')
                if changelog_url:
                    state.metadata_collector.collect("Changelog File", 'https://discovery.biothings.io/ns/maSMP/changeLog', changelog_url, 0.85)
        return state

class GitPlatformSoftwareRequirementExtractor(GitPlatformBaseExtractor):
    
    extracts = {'https://schema.org/softwareRequirements'}

    def extract(self, context, state):
        client = self.get_client(context, state)
        files = client.list_contents()
        found = []
        for file in files:
            if file.name.lower() in dependency_files:
                download_url = client.get_file(file.path).get('download_url')
                if download_url:
                    found.append(download_url)
        if len(found) > 0:
            state.metadata_collector.collect("Platform API", 'https://schema.org/softwareRequirements', found, 0.95)
        return state

class GitPlatformLicenseCopyrightHolderExtractor(GitPlatformBaseExtractor):
    """extracts the copyright holder and year from the license file"""

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
            year, holder = extract_copyright_holder(license.get_content() or "")
            if holder:
                state.metadata_collector.collect("License File", "https://schema.org/copyrightHolder", holder.strip(), 0.85)
            if year:
                try:
                    year = int(year)
                    state.metadata_collector.collect("License File", "https://schema.org/copyrightYear", year, 0.85)
                except:
                    pass
                
        return state 
    
class GitPlatformStorageReqExtractor(GitPlatformBaseExtractor):
    """extracts the copyright holder and year from the license file"""

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
            state.metadata_collector.collect('Platform API', "https://schema.org/storageRequirements", sizeStr, 0.95)
        return state

class GitPlatformDownloadUrlExtractor(GitPlatformBaseExtractor):
    """extracts the copyright holder and year from the license file"""

    extracts = {"https://schema.org/downloadUrl"}
    
    def extract(self, context, state):
        download_url = self.get_client(context, state).get_download_url()
        if download_url:
            state.metadata_collector.collect("Platform API", "https://schema.org/codeRepository", download_url, 0.95)
            state.metadata_collector.collect("Platform API", 'https://codemeta.github.io/terms/codeRepository', download_url, 0.95)
        return state