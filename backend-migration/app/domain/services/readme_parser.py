"""
Layer 3: Domain Services
README parser - extracts metadata from README files
"""
import re
from typing import Optional, List, Dict, Any
from app.core.entities.repository_metadata import RepositoryMetadata, ReferencePublication, Person


class ReadmeParser:
    """Parses README files to extract metadata"""
    
    def parse_readme(self, readme_content: str, metadata: RepositoryMetadata) -> RepositoryMetadata:
        """
        Parse README content to extract citations and authors.
        
        Args:
            readme_content: Content of the README file
            metadata: Current metadata object
            
        Returns:
            Updated metadata object
        """
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
        
        return metadata
    
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

