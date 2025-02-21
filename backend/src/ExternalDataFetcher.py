import requests
from src import Utilities

class ExternalDataFetcher():
    """
    A class responsible for fetching and processing metadata from external sources such as OpenAlex and archival services.
    """
    
    def __init__(self, repo_url, all_properties, DOI, access_token=None, reference_extracted=False):
        """
        Initializes the ExternalDataFetcher with necessary parameters.
        
        Args:
            repo_url (str): The URL of the repository.
            all_properties (dict): Dictionary containing metadata properties.
            DOI (str): Digital Object Identifier for the work.
            access_token (str, optional): Access token for authentication if required.
            reference_extracted (bool, optional): Flag indicating if references have been extracted. Defaults to False.
        """
        self.repo_url = repo_url
        self.owner, self.repo = Utilities.extract_repo_info(repo_url)
        self.all_properties = all_properties
        self.doi = DOI
        self.reference_extracted = reference_extracted
    
    def extract_archived_at(self, readme_url):
        """
        Extracts the archival URL for the repository by checking Zenodo badges or known archive services.
        
        Args:
            readme_url (str): The raw URL of the README file.
        
        Returns:
            str or None: The archival URL if found, otherwise None.
        """
        zenodo_links = Utilities.check_zenodo_badge(readme_url)
        if zenodo_links:
            return zenodo_links

        for base_url in ["https://archive.softwareheritage.org/browse/origin/directory/?origin_url=", "https://web.archive.org/web/"]:
            archive_url = f"{base_url}{self.repo_url}"
            if Utilities.is_valid_and_reachable(archive_url):
                return archive_url

        return None
    
    def extract(self):
        """
        Extracts metadata for the repository, including archival information, DOI-based metadata, and references.
        
        Returns:
            dict: Updated metadata properties.
        """
        for branch in ['master', 'main']:
            readme_raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/refs/heads/{branch}/README.md"
            archived_at = self.extract_archived_at(readme_raw_url)
            if archived_at:
                self.all_properties["archivedAt"] = archived_at
                break  

        if self.doi:
            response = self.fetch_openalex_metadata()
            openalex_authors = self.extract_authors(response)
            openalex_keywords = self.extract_keywords(response)
            
            if response.get('title') and not self.all_properties.get("alternateName"):
                self.all_properties["alternateName"] = response['title']
            
            if openalex_keywords:
                existing_keywords = self.all_properties.get("keywords", [])
                existing_keywords.extend(openalex_keywords)
                self.all_properties["keywords"] = list(set(existing_keywords))
            
            if openalex_authors:
                existing_authors = { (a["familyName"], a["givenName"]): a for a in self.all_properties.get("author", []) }
                for new_author in openalex_authors:
                    key = (new_author["familyName"], new_author["givenName"])
                    if key in existing_authors and "@id" not in existing_authors[key]:
                        existing_authors[key]["@id"] = new_author.get("@id")
                    else:
                        existing_authors[key] = new_author
                self.all_properties["author"] = list(existing_authors.values())

        if not self.reference_extracted:
            self.extract_doi_reference()

        return self.all_properties
    
    def fetch_openalex_metadata(self):
        """
        Fetches metadata associated with a DOI from the OpenAlex API.
        
        Returns:
            dict: JSON response containing metadata or error details.
        """
        url = f"https://api.openalex.org/works/doi:{self.doi}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        
    def extract_authors(self, response):
        """
        Extracts author details from an OpenAlex API response.
        
        Args:
            response (dict): JSON response from OpenAlex.
        
        Returns:
            list: List of authors in the required format.
        """
        authors = []
        if "authorships" in response:
            for author_entry in response["authorships"]:
                author = author_entry.get("author", {})
                if "display_name" in author:
                    given_name, family_name = author["display_name"].rsplit(" ", 1)
                    person = {
                        "@type": "Person",
                        "familyName": family_name,
                        "givenName": given_name
                    }
                    if "orcid" in author:
                        person["@id"] = author["orcid"]
                    authors.append(person)
        return authors
    
    def extract_keywords(self, response):
        """
        Extracts keywords from an OpenAlex API response.
        
        Args:
            response (dict): JSON response from OpenAlex.
        
        Returns:
            list: List of extracted keywords.
        """
        keywords = []
        if "keywords" in response:
            for keyword in response["keywords"]:
                if "display_name" in keyword:
                    keywords.append(keyword["display_name"])
        return keywords
    
    def extract_doi_reference(self):
        """
        Extracts DOI-based reference information and updates metadata properties.
        """
        response = self.fetch_openalex_metadata()
        reference_publication = {"@type": "ScholarlyArticle", "@id": f"https://doi.org/{self.doi}"}
        
        if response.get('title'):
            reference_publication['name'] = response['title']
        if (authors := self.extract_authors(response)):
            reference_publication['author'] = authors
        
        self.all_properties["codemeta:referencePublication"] = reference_publication
