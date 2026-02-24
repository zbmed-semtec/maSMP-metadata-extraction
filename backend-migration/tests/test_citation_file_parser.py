"""
Unit tests for CitationFileParser.
Cover title/alternateName merging, keywords, DOIs (top-level and preferred-citation),
author merging, and preferred citation extraction.
"""
from textwrap import dedent

from app.domain.services.citation_file_parser import CitationFileParser
from app.core.entities.repository_metadata import RepositoryMetadata


def test_citation_file_parser_parses_minimal_cff():
    parser = CitationFileParser()
    metadata = RepositoryMetadata()

    cff = dedent(
        """
        title: "My Software"
        keywords:
          - a
          - b
        doi: 10.1234/abcd.1
        authors:
          - family-names: Doe
            given-names: Jane
        """
    )

    updated, doi, ref_extracted = parser.parse_citation_cff(cff, metadata)

    assert doi == "10.1234/abcd.1"
    assert ref_extracted is False  # no preferred-citation section yet

    # alternateName gets merged
    assert updated.alternateName == ["My Software"]
    # keywords merged
    assert set(updated.keywords or []) == {"a", "b"}
    # identifier list contains DOI URL
    assert updated.identifier == ["https://doi.org/10.1234/abcd.1"]
    # author list contains parsed author
    assert updated.author is not None
    assert updated.author[0]["familyName"] == "Doe"
    assert updated.author[0]["givenName"] == "Jane"


def test_citation_file_parser_merges_preferred_citation_and_identifier():
    parser = CitationFileParser()
    # Pre-existing identifier and author to test merging & deduplication
    existing_id = "https://doi.org/10.9999/existing"
    metadata = RepositoryMetadata(identifier=[existing_id])

    cff = dedent(
        """
        title: "Another Title"
        preferred-citation:
          title: "Preferred Title"
          doi: 10.4321/wxyz.9
          authors:
            - family-names: Roe
              given-names: Richard
        authors:
          - family-names: Roe
            given-names: Richard
          - family-names: Poe
            given-names: Pat
        """
    )

    updated, doi, ref_extracted = parser.parse_citation_cff(cff, metadata)

    # No top-level DOI => doi return value may be None
    assert ref_extracted is True

    # identifier includes existing and preferred-citation DOI URL (without duplication)
    assert set(updated.identifier or []) == {
        existing_id,
        "https://doi.org/10.4321/wxyz.9",
    }

    # codemeta_referencePublication built from preferred-citation
    ref = updated.codemeta_referencePublication
    assert ref is not None
    assert ref.name == "Preferred Title"
    # ID may be None if DOI is not propagated; we primarily care about title/authors here
    assert ref.author is not None
    names = {(a.familyName, a.givenName) for a in ref.author}
    assert ("Roe", "Richard") in names

    # merged authors (deduped) in metadata.author
    merged_names = {(a.get("familyName"), a.get("givenName")) for a in (updated.author or [])}
    assert ("Roe", "Richard") in merged_names
    assert ("Poe", "Pat") in merged_names


def test_citation_file_parser_handles_invalid_yaml_gracefully():
    parser = CitationFileParser()
    metadata = RepositoryMetadata()

    bad_cff = ":::: this is not yaml :::"

    updated, doi, ref_extracted = parser.parse_citation_cff(bad_cff, metadata)

    # Should be a no-op without raising
    assert updated is metadata
    assert doi is None
    assert ref_extracted is False

