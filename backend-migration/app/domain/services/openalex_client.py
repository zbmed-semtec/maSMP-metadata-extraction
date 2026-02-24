"""
Layer 3: Domain Services
OpenAlex client - fetches metadata from OpenAlex API
"""
import requests
from typing import Optional, List, Dict, Any
from app.core.entities.repository_metadata import RepositoryMetadata


class OpenAlexClient:
    """Client for fetching metadata from OpenAlex API"""
    
    BASE_URL = "https://api.openalex.org/works"
    
    def fetch_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Fetch work metadata from OpenAlex by DOI.
        
        Args:
            doi: DOI identifier (with or without https://doi.org/)
            
        Returns:
            Work metadata dict or None if not found
        """
        # Clean DOI
        if doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")
        elif doi.startswith("doi:"):
            doi = doi.replace("doi:", "")
        
        url = f"{self.BASE_URL}/doi:{doi}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def extract_authors(self, work_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract authors from OpenAlex work data.
        
        Args:
            work_data: OpenAlex work JSON
            
        Returns:
            List of author dicts
        """
        authors = []
        if "authorships" not in work_data:
            return authors
        
        for author_entry in work_data["authorships"]:
            author = author_entry.get("author", {})
            if "display_name" in author:
                name_parts = author["display_name"].rsplit(" ", 1)
                if len(name_parts) == 2:
                    given_name, family_name = name_parts
                else:
                    given_name = author["display_name"]
                    family_name = ""
                
                person = {
                    "@type": "Person",
                    "familyName": family_name,
                    "givenName": given_name
                }
                
                if "orcid" in author and author["orcid"]:
                    person["@id"] = author["orcid"]
                
                authors.append(person)
        
        return authors
    
    def extract_keywords(self, work_data: Dict[str, Any]) -> List[str]:
        """
        Extract keywords from OpenAlex work data.
        
        Args:
            work_data: OpenAlex work JSON
            
        Returns:
            List of keywords
        """
        keywords = []
        if "keywords" in work_data:
            for keyword in work_data["keywords"]:
                if "display_name" in keyword:
                    keywords.append(keyword["display_name"])
        return keywords
    
    def enrich_metadata(self, metadata: RepositoryMetadata, doi: Optional[str] = None) -> RepositoryMetadata:
        """
        Enrich metadata with OpenAlex data.
        
        Args:
            metadata: Current metadata object
            doi: DOI to fetch data for
            
        Returns:
            Enriched metadata object
        """
        if not doi:
            # Try to extract DOI from identifier (which may now be a list of URLs)
            id_value = metadata.identifier
            candidate: Optional[str] = None
            if isinstance(id_value, list):
                candidate = next((v for v in id_value if isinstance(v, str) and "doi.org" in v), None)
            elif isinstance(id_value, str) and "doi.org" in id_value:
                candidate = id_value

            if candidate:
                doi = candidate.replace("https://doi.org/", "")
            else:
                return metadata
        
        work_data = self.fetch_work_by_doi(doi)
        if not work_data:
            return metadata
        
        # Extract title if not already set
        if work_data.get("title") and not metadata.alternateName:
            metadata.alternateName = work_data["title"]
        
        # Extract and merge keywords
        openalex_keywords = self.extract_keywords(work_data)
        if openalex_keywords:
            existing_keywords = metadata.keywords or []
            existing_keywords.extend(openalex_keywords)
            metadata.keywords = list(set(existing_keywords))
        
        # Extract and merge authors
        openalex_authors = self.extract_authors(work_data)
        if openalex_authors:
            # Use (familyName, givenName) tuple as a stable key
            existing_authors = {
                (a.get("familyName", ""), a.get("givenName", "")): a
                for a in (metadata.author or [])
            }
            for new_author in openalex_authors:
                key = (new_author.get("familyName", ""), new_author.get("givenName", ""))
                if key in existing_authors and "@id" not in existing_authors[key]:
                    existing_authors[key]["@id"] = new_author.get("@id")
                else:
                    existing_authors[key] = new_author
            metadata.author = list(existing_authors.values())
        
        return metadata

