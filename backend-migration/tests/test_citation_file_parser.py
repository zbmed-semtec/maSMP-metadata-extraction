"""
Unit tests for CitationCffWorkflow.
Cover title/alternateName merging, keywords, DOIs (top-level and preferred-citation),
author merging, and preferred citation extraction.
"""
from __future__ import annotations
from textwrap import dedent

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.extract_steps.services.files.workflows import CitationCffWorkflow


def test_citation_file_parser_parses_minimal_cff():
    workflow = CitationCffWorkflow()
    metadata = SoftwareMetadata()

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

    updated, doi, ref_extracted = workflow.run(cff, metadata)

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
    workflow = CitationCffWorkflow()
    # Pre-existing identifier and author to test merging & deduplication
    existing_id = "https://doi.org/10.9999/existing"
    metadata = SoftwareMetadata(identifier=[existing_id])

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

    updated, doi, ref_extracted = workflow.run(cff, metadata)

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
    workflow = CitationCffWorkflow()
    metadata = SoftwareMetadata()

    bad_cff = ":::: this is not yaml :::"

    updated, doi, ref_extracted = workflow.run(bad_cff, metadata)

    # Should be a no-op without raising
    assert updated is metadata
    assert doi is None
    assert ref_extracted is False


def test_citation_file_parser_resolves_metadata_links_with_runtime_context():
    workflow = CitationCffWorkflow()
    metadata = SoftwareMetadata()

    cff = dedent(
        """
        title: "Runtime Context Demo"
        """
    )

    def _is_reachable(url: str) -> bool:
        return url.endswith("/blob/main/README.md")

    updated, doi, ref_extracted = workflow.run(
        cff,
        metadata,
        repo_url="https://github.com/org/repo/",
        platform="github",
        is_file_reachable_fn=_is_reachable,
    )

    assert doi is None
    assert ref_extracted is False
    assert updated.codemeta_readme == "https://github.com/org/repo/blob/main/README.md"

