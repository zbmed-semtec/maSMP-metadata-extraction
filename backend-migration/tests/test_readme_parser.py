"""
Unit tests for ReadmeExtractionWorkflow.
Cover DOI extraction (including Zenodo IDs), BibTeX parsing, author merging, and edge cases.
"""
from __future__ import annotations
from app.layer_1.entities.shared_primitives import Person
from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.license import ExtractLicenseCopyrightStep
from app.layer_3.steps.extract_steps.services.files.workflows import ReadmeExtractionWorkflow


def test_readme_parser_extracts_doi_and_sets_identifier_flag():
    workflow = ReadmeExtractionWorkflow()
    metadata = SoftwareMetadata()

    content = """
    This project has a DOI badge:
    https://doi.org/10.1234/abcd.1
    """

    updated, identifier_set = workflow.run(content, metadata)

    assert identifier_set is True
    assert updated.identifier == ["https://doi.org/10.1234/abcd.1"]


def test_readme_parser_extracts_zenodo_badge_and_converts_to_doi():
    workflow = ReadmeExtractionWorkflow()
    metadata = SoftwareMetadata()

    content = """
    Zenodo badge:
    https://zenodo.org/record/987654
    """

    updated, identifier_set = workflow.run(content, metadata)

    assert identifier_set is True
    # Zenodo id must be converted into a DOI with 10.5281/zenodo.<id>
    assert updated.identifier == ["https://doi.org/10.5281/zenodo.987654"]


def test_readme_parser_does_not_duplicate_existing_identifier():
    workflow = ReadmeExtractionWorkflow()
    metadata = SoftwareMetadata(identifier=["https://doi.org/10.1234/abcd.1"])

    content = """
    Duplicate DOI:
    https://doi.org/10.1234/abcd.1
    """

    updated, identifier_set = workflow.run(content, metadata)

    assert identifier_set is True
    # No duplicate entries should be added
    assert updated.identifier == ["https://doi.org/10.1234/abcd.1"]


def test_readme_parser_extracts_bibtex_and_merges_authors():
    workflow = ReadmeExtractionWorkflow()
    # Pre-existing author should be preserved and deduped
    existing_author = {"@type": "Person", "familyName": "Doe", "givenName": "Jane"}
    metadata = SoftwareMetadata(author=[existing_author])

    content = r"""
    ```bibtex
    @article{key,
      title = {Some Title},
      author = {Doe Jane and Smith John}
    }
    ```
    """

    updated, identifier_set = workflow.run(content, metadata)

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


def test_license_step_extracts_copyright():
    text = "Copyright (c) 2024 Example Org"
    step = ExtractLicenseCopyrightStep()
    state = StepState(metadata=SoftwareMetadata(), data={"license_content": text})
    context = StepContext(repo_url="", domain="software", schema="maSMP")

    result = step.run(context, state)
    assert result.data["extracted_license_copyright_holder"] == "Example Org"

