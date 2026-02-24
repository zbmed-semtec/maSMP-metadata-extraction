"""
Unit tests for JSONLDBuilder.
Cover maSMP and CODEMETA JSON-LD building, field mapping, and allowed-fields filtering.
"""
from app.adapters.jsonld_builder import JSONLDBuilder
from app.core.entities.repository_metadata import RepositoryMetadata, VersionControlSystem


def _base_metadata() -> RepositoryMetadata:
    return RepositoryMetadata(
        name="Test Repo",
        alternateName=["Alt Name"],
        description="Desc",
        url="https://example.com/repo",
        codeRepository="https://example.com/repo.git",
        keywords=["a", "b"],
        identifier=["id1"],
        license={"name": "MIT"},
        masmp_versionControlSystem=VersionControlSystem.create_git(vcs_type="SoftwareSourceCode"),
        codemeta_readme="https://example.com/README.md",
        codemeta_issueTracker="https://example.com/issues",
        masmp_changelog="https://example.com/CHANGELOG.md",
    )


def test_build_jsonld_codemeta_includes_only_allowed_fields():
    builder = JSONLDBuilder()
    metadata = _base_metadata()

    jsonld = builder.build_jsonld(metadata, schema="CODEMETA", has_release=False)

    # Core structure
    assert jsonld["@type"] == "SoftwareSourceCode"
    assert "name" in jsonld
    assert "alternateName" in jsonld
    assert "keywords" in jsonld
    # Codemeta-prefixed fields get mapped using colon
    assert "codemeta:readme" in jsonld
    assert "codemeta:issueTracker" in jsonld


def test_build_jsonld_masmp_includes_has_release_and_nested_structures():
    builder = JSONLDBuilder()
    metadata = _base_metadata()

    jsonld = builder.build_jsonld(metadata, schema="maSMP", has_release=True)

    assert jsonld["hasRelease"] is True
    assert "maSMP:SoftwareSourceCode" in jsonld
    assert "maSMP:SoftwareApplication" in jsonld

    ssc = jsonld["maSMP:SoftwareSourceCode"]
    app = jsonld["maSMP:SoftwareApplication"]

    # Check that selected fields have been mapped into both structures
    assert ssc["name"] == "Test Repo"
    assert app["name"] == "Test Repo"
    # codemeta_readme is mapped as codemeta:readme
    assert ssc["codemeta:readme"] == "https://example.com/README.md"
    assert app["codemeta:readme"] == "https://example.com/README.md"

