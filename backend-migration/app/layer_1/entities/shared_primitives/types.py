"""
Shared value objects used across domain entities (e.g. software, future training).

No dependencies on other entity modules.
"""
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


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
        populate_by_name = True


class VersionControlSystem(BaseModel):
    """Version control system (e.g. Git) for software metadata / maSMP."""

    type: Optional[str] = Field(default="SoftwareSourceCode", alias="@type")
    id: Optional[str] = Field(default=None, alias="@id")
    url: Optional[HttpUrl] = None
    name: Optional[str] = None

    class Config:
        populate_by_name = True

    @classmethod
    def create_git(cls, vcs_type: str = "SoftwareSourceCode") -> "VersionControlSystem":
        return cls(
            type=vcs_type,
            id="https://www.wikidata.org/wiki/Q186055",
            url="https://git-scm.com/",
            name="Git",
        )


class License(BaseModel):
    """Software license name and URL."""

    name: Optional[str] = None
    url: Optional[HttpUrl] = None

    class Config:
        populate_by_name = True


class ReferencePublication(BaseModel):
    """Scholarly work (e.g. codemeta:referencePublication)."""

    type: Optional[str] = Field(default="ScholarlyArticle", alias="@type")
    id: Optional[str] = Field(default=None, alias="@id")
    name: Optional[str] = None
    author: Optional[List[Person]] = None

    class Config:
        populate_by_name = True
