"""
Layer 3: Domain Services
Citation file parser - parses CITATION.cff files
"""
import yaml
from typing import Optional, Dict, Any, List
from app.core.entities.repository_metadata import RepositoryMetadata, ReferencePublication, Person


class CitationFileParser:
    """Parses CITATION.cff files from repositories"""
    
    def parse_citation_cff(self, cff_content: str, metadata: RepositoryMetadata) -> tuple[RepositoryMetadata, Optional[str], bool]:
        """
        Parse CITATION.cff content and update metadata.
        
        Args:
            cff_content: Content of the CITATION.cff file
            metadata: Current metadata object
            
        Returns:
            tuple: (updated_metadata, doi, reference_extracted)
        """
        try:
            cff_data = yaml.safe_load(cff_content)
        except yaml.YAMLError:
            return metadata, None, False
        
        if not cff_data:
            return metadata, None, False
        
        # Extract basic fields
        if "title" in cff_data:
            metadata.alternateName = cff_data["title"]
        
        if "keywords" in cff_data and isinstance(cff_data["keywords"], list):
            existing = metadata.keywords or []
            metadata.keywords = list(set(existing) | set(cff_data["keywords"]))
        
        # Extract DOI(s)
        doi: Optional[str] = None
        identifier_values = list(metadata.identifier or [])
        
        # Top-level DOI (if present)
        if "doi" in cff_data and cff_data["doi"]:
            doi = str(cff_data["doi"])
            doi_url = f"https://doi.org/{doi}"
            if doi_url not in identifier_values:
                identifier_values.append(doi_url)
            if not metadata.citation:
                metadata.citation = []
            metadata.citation.append({
                "@type": "Article",
                "@id": doi_url,
            })
        
        # Preferred-citation DOI (may be present even when top-level doi is absent)
        preferred = cff_data.get("preferred-citation") or {}
        pref_doi = preferred.get("doi")
        if pref_doi:
            pref_doi_str = str(pref_doi)
            pref_doi_url = f"https://doi.org/{pref_doi_str}"
            if pref_doi_url not in identifier_values:
                identifier_values.append(pref_doi_url)
        
        # Extract authors
        if "authors" in cff_data:
            authors = []
            for author in cff_data["authors"]:
                person = {
                    "@type": "Person",
                    "familyName": author.get("family-names"),
                    "givenName": author.get("given-names")
                }
                if "orcid" in author:
                    person["@id"] = author["orcid"]
                authors.append(person)
            metadata.author = authors
        
        if identifier_values:
            metadata.identifier = identifier_values

        # Extract preferred citation object
        reference_extracted = False
        if preferred:
            self._extract_preferred_citation(preferred, metadata)
            reference_extracted = True

        return metadata, doi, reference_extracted
    
    def _extract_preferred_citation(self, preferred_citation: Dict[str, Any], metadata: RepositoryMetadata):
        """Extract preferred citation from CITATION.cff"""
        authors: List[Person] = []
        
        if "authors" in preferred_citation and preferred_citation["authors"]:
            for author in preferred_citation["authors"]:
                author_obj = Person(
                    type="Person",
                    familyName=author.get("family-names"),
                    givenName=author.get("given-names"),
                )
                if "orcid" in author:
                    author_obj.id = author["orcid"]
                authors.append(author_obj)
        
        metadata.codemeta_referencePublication = ReferencePublication(
            type="ScholarlyArticle",
            id=f"https://doi.org/{preferred_citation['doi']}" if preferred_citation.get("doi") else None,
            name=preferred_citation.get("title"),
            author=authors if authors else None
        )

