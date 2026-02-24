"""
Layer 3: Domain Services
README parser - extracts metadata from README files
"""
import re
from typing import Optional, List, Dict, Any, Tuple
from app.core.entities.repository_metadata import RepositoryMetadata, ReferencePublication, Person


# Pattern for DOI URLs (e.g. in badges or links: https://doi.org/10.1234/xyz or https://zenodo.org/records/123)
_DOI_URL_PATTERN = re.compile(
    r"https://(?:doi\.org/([^\s\)\]\"']+)|zenodo\.org/records?/(\d+))",
    re.IGNORECASE,
)


class ReadmeParser:
    """Parses README files to extract metadata"""

    def parse_readme(
        self, readme_content: str, metadata: RepositoryMetadata
    ) -> Tuple[RepositoryMetadata, bool]:
        """
        Parse README content to extract citations, authors, and identifier (DOI from badges/links).

        Args:
            readme_content: Content of the README file
            metadata: Current metadata object

        Returns:
            (updated_metadata, identifier_was_set_from_readme)
            identifier_was_set_from_readme is True when a DOI was found in the README and used to set metadata.identifier.
        """
        identifier_set_by_readme = False

        # Extract identifier from DOI badge or link in README (e.g. Zenodo/DOI badge)
        for match in _DOI_URL_PATTERN.finditer(readme_content):
            if match.group(1):
                doi = match.group(1)
            else:
                doi = f"10.5281/zenodo.{match.group(2)}"
            # Merge with any existing identifiers; allow multiple DOIs (article + software)
            existing_ids = list(metadata.identifier or [])
            doi_url = f"https://doi.org/{doi}"
            if doi_url not in existing_ids:
                existing_ids.append(doi_url)
            metadata.identifier = existing_ids
            identifier_set_by_readme = True
            break

        # Extract BibTeX citations
        citations = re.findall(r'```bibtex([\s\S]*?)```', readme_content)
        
        if citations:
            # Use the first citation found as the reference publication
            # (can be extended to support multiple publications if needed)
            citation = citations[0]
            all_authors = []
            
            # Extract title
            title_match = re.search(r'title\s*=\s*[{"](.*?)[}"]', citation, re.IGNORECASE)
            title = title_match.group(1) if title_match else None
            
            # Extract authors
            author_matches = re.findall(r'author\s*=\s*[{"](.*?)[}"]', citation, re.IGNORECASE)
            authors: List[Person] = []
            for author_str in author_matches:
                for author in author_str.split(" and "):
                    author_parts = author.strip().split(" ")
                    author_obj = Person(
                        type="Person",
                        familyName=author_parts[0].strip() if len(author_parts) > 0 else None,
                        givenName=author_parts[1].strip() if len(author_parts) > 1 else None,
                    )
                    authors.append(author_obj)
                    all_authors.append(author_obj)
            
            # Update metadata if not already set
            if not metadata.codemeta_referencePublication and (title or authors):
                metadata.codemeta_referencePublication = ReferencePublication(
                    type="ScholarlyArticle",
                    name=title,
                    author=authors if authors else None
                )
            
            # Update authors if not already set
            if all_authors and not metadata.author:
                # Remove duplicates based on name
                seen = set()
                unique_authors = []
                for author in all_authors:
                    key = (author.familyName, author.givenName)
                    if key not in seen:
                        seen.add(key)
                        unique_authors.append(author)
                metadata.author = unique_authors

        return metadata, identifier_set_by_readme
    
    def extract_license_copyright(self, license_content: str) -> Optional[str]:
        """
        Extract copyright holder from LICENSE file.
        
        Args:
            license_content: Content of the LICENSE file
            
        Returns:
            Copyright holder name or None
        """
        match = re.search(r"Copyright\s+\([cC]\)\s+\d{4}\s+(.+)", license_content)
        if match:
            return match.group(1).strip()
        return None

