import re
import yaml
from src.logger_config import logger
from src import Utilities

class RepoFilesParser():
    """
    A class to parse important metadata files from a GitHub repository, such as CITATION.cff and LICENSE.
    """
    def __init__(self, repo_url, all_properties, access_token=None):
        """
        Initializes the RepoFilesParser instance.
        
        Args:
            repo_url (str): The URL of the GitHub repository.
            all_properties (dict): A dictionary to store extracted metadata.
            access_token (str, optional): GitHub access token for authentication.
        """
        self.repo_url = repo_url
        self.access_token = access_token
        self.owner, self.repo = Utilities.extract_repo_info(repo_url)
        self.base_url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contents'
        self.all_properties = all_properties
        self.doi = None
        self.reference_extracted = False

    def parse_files(self):
        """
        Parses citation and license files from the repository.
        
        Returns:
            tuple: Updated all_properties dictionary, DOI (if found), and reference_extracted status.
        """
        self.parse_citation_cff()
        self.parse_license_file()
        return self.all_properties, self.doi, self.reference_extracted

    def get_citation_filedata(self):
        """
        Fetches and parses the CITATION.cff file if it exists in the repository.
        
        Returns:
            dict or None: Parsed YAML content of the CITATION.cff file, or None if not found.
        """
        citation_filenames = {'CITATION.cff', 'citation.cff'}
        
        response = Utilities.fetch_github_file(self.base_url, self.access_token)
        
        if response.status_code != 200:
            logger.warning(f"Failed to fetch repository contents: {response.status_code}")
            return None
        
        try:
            repo_contents = response.json()
        except ValueError:
            logger.warning("Invalid JSON response from GitHub API")
            return None
        
        for file in repo_contents:
            if file['name'] in citation_filenames:
                cff_url = file['download_url']
                file_response = Utilities.fetch_github_file(cff_url, self.access_token)
                
                if file_response.status_code == 200:
                    try:
                        return yaml.safe_load(file_response.text)
                    except yaml.YAMLError as e:
                        logger.warning(f"Unable to parse citation.cff file: {e}")
                        return None
        
        logger.warning("CITATION.cff file not found.")
        return None
    
    def parse_citation_cff(self):
        """
        Extracts metadata from the CITATION.cff file and updates all_properties.
        """
        cff_data = self.get_citation_filedata()
        
        if not cff_data:
            return
        
        target_keys = {
            "alternateName": "title",
            "identifier": "doi",
            "keywords": "keywords"
        }
        
        self.all_properties["citation"] = []
        
        for property_name, target_key in target_keys.items():
            values = Utilities.find_property(cff_data, target_key)
            if values:
                self.doi = values[0]
                if property_name == "identifier":
                    self.all_properties[property_name] = f"https://doi.org/{values[0]}"
                    self.all_properties["citation"].append({"@type":"Article", "@id": f"https://doi.org/{values[0]}"})
                else:
                    self.all_properties[property_name] = values[0]
        
        authors = []
        if 'authors' in cff_data:
            for author in cff_data['authors']:
                person = {
                    "@type": "Person",
                    "familyName": author.get('family-names'),
                    "givenName": author.get('given-names')
                }
                if 'orcid' in author:
                    person["@id"] = author['orcid']
                authors.append(person)
        
        if authors:
            self.all_properties["author"] = authors
        
        if 'preferred-citation' in cff_data:
            self.extract_preferred_citation(cff_data['preferred-citation'])
            self.reference_extracted = True

    def extract_preferred_citation(self, preferred_citation):
        """
        Extracts the preferred citation from the CITATION.cff file.
        
        Args:
            preferred_citation (dict): Preferred citation data extracted from CITATION.cff.
        """
        reference_publication = {"@type": "ScholarlyArticle"}
        
        if 'doi' in preferred_citation:
            reference_publication["@id"] = f"https://doi.org/{preferred_citation['doi']}"
        if 'title' in preferred_citation:
            reference_publication['name'] = preferred_citation['title']
        if 'authors' in preferred_citation:
            reference_publication['author'] = []
            for author in preferred_citation['authors']:
                author_entry = {
                    "@type": "Person",
                    "familyName": author.get('family-names'),
                    "givenName": author.get('given-names'),
                }
                if 'orcid' in author:
                    author_entry["@id"] = author['orcid']
                reference_publication["author"].append(author_entry)
        
        self.all_properties["codemeta:referencePublication"] = reference_publication

    def parse_license_file(self):
        """
        Extracts the copyright holder information from the LICENSE file if available.
        """
        for branch in ['master', 'main']:
            license_url = f'https://raw.githubusercontent.com/{self.owner}/{self.repo}/{branch}/LICENSE'
            response = Utilities.fetch_github_file(license_url, self.access_token)
            license_content = response.text
            match = re.search(r"Copyright\s+\([cC]\)\s+\d{4}\s+(.+)", license_content)
            if match:
                self.all_properties["copyrightHolder"] = match.group(1)
                break
