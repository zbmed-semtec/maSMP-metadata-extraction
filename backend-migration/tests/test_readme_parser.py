"""
Unit tests for ReadmeParser.
Cover DOI extraction (including Zenodo IDs), BibTeX parsing, author merging, and edge cases.
"""
from app.domain.services.readme_parser import ReadmeParser
from app.core.entities.repository_metadata import RepositoryMetadata, Person


def test_readme_parser_extracts_doi_and_sets_identifier_flag():
    parser = ReadmeParser()
    metadata = RepositoryMetadata()

    content = """
    This project has a DOI badge:
    https://doi.org/10.1234/abcd.1
    """

    updated, identifier_set = parser.parse_readme(content, metadata)

    assert identifier_set is True
    assert updated.identifier == ["https://doi.org/10.1234/abcd.1"]


def test_readme_parser_extracts_zenodo_badge_and_converts_to_doi():
    parser = ReadmeParser()
    metadata = RepositoryMetadata()

    content = """
    Zenodo badge:
    https://zenodo.org/record/987654
    """

    updated, identifier_set = parser.parse_readme(content, metadata)

    assert identifier_set is True
    # Zenodo id must be converted into a DOI with 10.5281/zenodo.<id>
    assert updated.identifier == ["https://doi.org/10.5281/zenodo.987654"]


def test_readme_parser_does_not_duplicate_existing_identifier():
    parser = ReadmeParser()
    metadata = RepositoryMetadata(identifier=["https://doi.org/10.1234/abcd.1"])

    content = """
    Duplicate DOI:
    https://doi.org/10.1234/abcd.1
    """

    updated, identifier_set = parser.parse_readme(content, metadata)

    assert identifier_set is True
    # No duplicate entries should be added
    assert updated.identifier == ["https://doi.org/10.1234/abcd.1"]


def test_readme_parser_extracts_bibtex_and_merges_authors():
    parser = ReadmeParser()
    # Pre-existing author should be preserved and deduped
    existing_author = {"@type": "Person", "familyName": "Doe", "givenName": "Jane"}
    metadata = RepositoryMetadata(author=[existing_author])

    content = r"""
    ```bibtex
    @article{key,
      title = {Some Title},
      author = {Doe Jane and Smith John}
    }
    ```
    """

    updated, identifier_set = parser.parse_readme(content, metadata)

    assert identifier_set is False

    # Reference publication should be set from BibTeX
    assert updated.codemeta_referencePublication is not None
    assert updated.codemeta_referencePublication.name == "Some Title"
    assert updated.codemeta_referencePublication.author is not None

    # Authors should be merged and deduplicated by (familyName, givenName)
    names = {(a.familyName, a.givenName) if isinstance(a, Person) else (a.get("familyName"), a.get("givenName"))
             for a in (updated.author or [])}
    assert ("Doe", "Jane") in names
    assert ("Smith", "John") in names


def test_readme_parser_extracts_copyright():
    parser = ReadmeParser()
    text = "Copyright (c) 2024 Example Org"

    holder = parser.extract_license_copyright(text)
    assert holder == "Example Org"

