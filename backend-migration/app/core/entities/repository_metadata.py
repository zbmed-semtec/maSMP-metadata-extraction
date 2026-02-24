"""
Layer 1: Core Entities
The innermost layer - contains only the final data model.
No dependencies on other layers.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class Person(BaseModel):
    """Represents a person (author, contributor, maintainer, etc.)"""
    type: Optional[str] = Field(default="Person", alias="@type")
    name: Optional[str] = None
    givenName: Optional[str] = None
    familyName: Optional[str] = None
    url: Optional[HttpUrl] = None
    id: Optional[str] = Field(default=None, alias="@id")
    email: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True


class VersionControlSystem(BaseModel):
    """
    Represents a version control system.
    
    Used in maSMP profiles (SoftwareSourceCode and SoftwareApplication).
    The @type can be "SoftwareSourceCode" or "SoftwareApplication" depending on context.
    """
    type: Optional[str] = Field(default="SoftwareSourceCode", alias="@type")
    id: Optional[str] = Field(default=None, alias="@id")  # Wikidata URL
    url: Optional[HttpUrl] = None  # Tool URL (e.g., https://git-scm.com/)
    name: Optional[str] = None  # Name (e.g., "Git")
    
    class Config:
        allow_population_by_field_name = True
    
    @classmethod
    def create_git(cls, vcs_type: str = "SoftwareSourceCode") -> "VersionControlSystem":
        """
        Factory method to create a Git version control system.
        
        Args:
            vcs_type: Type for maSMP profile - "SoftwareSourceCode" or "SoftwareApplication"
            
        Returns:
            VersionControlSystem instance for Git
        """
        return cls(
            type=vcs_type,
            id="https://www.wikidata.org/wiki/Q186055",
            url="https://git-scm.com/",
            name="Git"
        )


class License(BaseModel):
    """
    Represents a software license.
    
    Contains license name and URL.
    """
    name: Optional[str] = None  # License name (e.g., "MIT License")
    url: Optional[HttpUrl] = None  # License URL (e.g., "https://api.github.com/licenses/mit")
    
    class Config:
        allow_population_by_field_name = True


class ReferencePublication(BaseModel):
    """
    Represents a scholarly article or reference publication.
    
    Used in codemeta:referencePublication field.
    Contains publication metadata including DOI, title, and authors.
    """
    type: Optional[str] = Field(default="ScholarlyArticle", alias="@type")
    id: Optional[str] = Field(default=None, alias="@id")  # DOI URL (e.g., "https://doi.org/10.1162/qss_a_00167")
    name: Optional[str] = None  # Publication title
    author: Optional[List[Person]] = None  # List of authors (Person objects)
    
    class Config:
        allow_population_by_field_name = True


class RepositoryMetadata(BaseModel):
    """
    The core entity representing repository metadata.
    Contains all 30+ fields that can be extracted from any platform.
    This is the ONLY model in Layer 1.
    """
    # Basic Information
    name: Optional[str] = None
    # Multiple alternate names (e.g., from CITATION.cff title, OpenAlex title, etc.)
    alternateName: Optional[List[str]] = None
    description: Optional[str] = None
    version: Optional[str] = None
    softwareVersion: Optional[str] = None
    
    # Repository Information
    codeRepository: Optional[str] = None
    url: Optional[HttpUrl] = None
    downloadUrl: Optional[HttpUrl] = None
    hasSourceCode: Optional[str] = None
    codemeta_hasSourceCode: Optional[str] = None
    
    # People
    author: Optional[List[Dict[str, Any]]] = None
    contributor: Optional[List[Dict[str, Any]]] = None
    maintainer: Optional[List[Dict[str, Any]]] = None
    copyrightHolder: Optional[str] = None
    
    # Dates
    dateCreated: Optional[str] = None
    dateModified: Optional[str] = None
    datePublished: Optional[str] = None
    
    # Technical Details
    programmingLanguage: Optional[List[str]] = None
    runtimePlatform: Optional[List[str]] = None
    operatingSystem: Optional[List[str]] = None
    softwareRequirements: Optional[List[str]] = None
    memoryRequirements: Optional[str] = None
    processorRequirements: Optional[str] = None
    storageRequirements: Optional[str] = None
    
    # License & Access
    license: Optional[License] = None
    isAccessibleForFree: Optional[str] = None
    conditionsOfAccess: Optional[str] = None
    
    # Documentation & Resources
    documentation: Optional[HttpUrl] = None
    codemeta_readme: Optional[str] = None
    codemeta_buildInstructions: Optional[str] = None
    masmp_developerDocumentation: Optional[str] = None
    masmp_userDocumentation: Optional[str] = None
    masmp_learningResource: Optional[str] = None
    masmp_installInstructions: Optional[str] = None
    masmp_deployInstructions: Optional[str] = None
    masmp_testInstructions: Optional[str] = None
    masmp_changelog: Optional[str] = None
    
    # Metadata
    # identifier can have multiple values (e.g., software DOI, article DOI, SWHID)
    # We model it as a list of strings to allow merging identifiers from
    # different sources such as CITATION.cff and README badges.
    identifier: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    citation: Optional[List[Dict[str, Any]]] = None
    codemeta_referencePublication: Optional[ReferencePublication] = None
    
    # Version Control
    masmp_versionControlSystem: Optional[VersionControlSystem] = None
    
    # Issue Tracking & Discussion
    issueTracker: Optional[HttpUrl] = None
    codemeta_issueTracker: Optional[HttpUrl] = None
    discussionUrl: Optional[HttpUrl] = None
    
    # Release Information
    releaseNotes: Optional[str] = None
    codemeta_developmentStatus: Optional[str] = None
    
    # Archive Information
    archivedAt: Optional[str] = None
    
    # Additional maSMP fields
    masmp_intendedUse: Optional[str] = None
    codeSampleType: Optional[str] = None
    applicationCategory: Optional[str] = None
    
    # Media
    image: Optional[HttpUrl] = None
    logo: Optional[HttpUrl] = None
    
    # Additional fields that may come from external sources
    funders: Optional[List[Dict[str, Any]]] = None
    doi: Optional[str] = None
    
    # Internal flag for release status (not part of final JSON-LD)
    has_release: bool = False
    
    class Config:
        """Pydantic configuration"""
        # Allow fields with @ prefix (like @type, @id)
        allow_population_by_field_name = True
        # Store extra fields that don't match the model
        extra = "allow"

