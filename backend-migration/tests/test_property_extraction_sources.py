"""
Tests that each metadata property is documented to flow through the correct
extraction sources, and that adapters only record (property, source) pairs
allowed by the registry.

Run with: pytest backend-migration/tests/test_property_extraction_sources.py -v
"""
import pytest

from app.domain.extraction_sources import (
    SOURCE_GITHUB_API,
    SOURCE_GITLAB_API,
    SOURCE_CITATION_CFF,
    SOURCE_LICENSE_FILE,
    SOURCE_README_PARSER,
    SOURCE_ZENODO_BADGE,
    SOURCE_WAYBACK,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_OPENALEX,
)
from app.domain.property_extraction_sources import (
    PROPERTY_EXTRACTION_SOURCES,
    ALL_SOURCES,
    get_sources_for_property,
    get_properties_for_source,
)


# (property, source) pairs that adapters are expected to record.
# When adding a new record() in an adapter, add the pair here and to the registry.
EXPECTED_ADAPTER_RECORDINGS = [
    # GitHub extractor
    ("name", SOURCE_GITHUB_API),
    ("description", SOURCE_GITHUB_API),
    ("url", SOURCE_GITHUB_API),
    ("codeRepository", SOURCE_GITHUB_API),
    ("dateCreated", SOURCE_GITHUB_API),
    ("dateModified", SOURCE_GITHUB_API),
    ("datePublished", SOURCE_GITHUB_API),
    ("conditionsOfAccess", SOURCE_GITHUB_API),
    ("isAccessibleForFree", SOURCE_GITHUB_API),
    ("issueTracker", SOURCE_GITHUB_API),
    ("codemeta_issueTracker", SOURCE_GITHUB_API),
    ("discussionUrl", SOURCE_GITHUB_API),
    ("downloadUrl", SOURCE_GITHUB_API),
    ("hasSourceCode", SOURCE_GITHUB_API),
    ("codemeta_hasSourceCode", SOURCE_GITHUB_API),
    ("keywords", SOURCE_GITHUB_API),
    ("masmp_versionControlSystem", SOURCE_GITHUB_API),
    ("programmingLanguage", SOURCE_GITHUB_API),
    ("contributor", SOURCE_GITHUB_API),
    ("license", SOURCE_GITHUB_API),
    ("codemeta_readme", SOURCE_GITHUB_API),
    ("masmp_changelog", SOURCE_GITHUB_API),
    ("softwareVersion", SOURCE_GITHUB_API),
    ("version", SOURCE_GITHUB_API),
    # GitLab extractor (same set of fields)
    ("name", SOURCE_GITLAB_API),
    ("description", SOURCE_GITLAB_API),
    ("url", SOURCE_GITLAB_API),
    ("codeRepository", SOURCE_GITLAB_API),
    ("dateCreated", SOURCE_GITLAB_API),
    ("dateModified", SOURCE_GITLAB_API),
    ("datePublished", SOURCE_GITLAB_API),
    ("conditionsOfAccess", SOURCE_GITLAB_API),
    ("isAccessibleForFree", SOURCE_GITLAB_API),
    ("issueTracker", SOURCE_GITLAB_API),
    ("codemeta_issueTracker", SOURCE_GITLAB_API),
    ("discussionUrl", SOURCE_GITLAB_API),
    ("downloadUrl", SOURCE_GITLAB_API),
    ("hasSourceCode", SOURCE_GITLAB_API),
    ("codemeta_hasSourceCode", SOURCE_GITLAB_API),
    ("keywords", SOURCE_GITLAB_API),
    ("masmp_versionControlSystem", SOURCE_GITLAB_API),
    ("programmingLanguage", SOURCE_GITLAB_API),
    ("contributor", SOURCE_GITLAB_API),
    ("license", SOURCE_GITLAB_API),
    ("codemeta_readme", SOURCE_GITLAB_API),
    ("masmp_changelog", SOURCE_GITLAB_API),
    ("softwareVersion", SOURCE_GITLAB_API),
    ("version", SOURCE_GITLAB_API),
    # File parser: CITATION.cff
    ("alternateName", SOURCE_CITATION_CFF),
    ("keywords", SOURCE_CITATION_CFF),
    ("identifier", SOURCE_CITATION_CFF),
    ("citation", SOURCE_CITATION_CFF),
    ("author", SOURCE_CITATION_CFF),
    ("codemeta_referencePublication", SOURCE_CITATION_CFF),
    # File parser: LICENSE
    ("copyrightHolder", SOURCE_LICENSE_FILE),
    # File parser: README
    ("codemeta_readme", SOURCE_README_PARSER),
    ("identifier", SOURCE_README_PARSER),
    ("codemeta_referencePublication", SOURCE_README_PARSER),
    ("author", SOURCE_README_PARSER),
    # External: Zenodo / Wayback / Software Heritage
    ("archivedAt", SOURCE_ZENODO_BADGE),
    ("archivedAt", SOURCE_WAYBACK),
    ("archivedAt", SOURCE_SOFTWARE_HERITAGE),
    # External: OpenAlex
    ("alternateName", SOURCE_OPENALEX),
    ("keywords", SOURCE_OPENALEX),
    ("author", SOURCE_OPENALEX),
    ("codemeta_referencePublication", SOURCE_OPENALEX),
]


def _registry_pairs():
    """All (property, source) pairs allowed by the registry."""
    for prop, sources in PROPERTY_EXTRACTION_SOURCES.items():
        for source in sources:
            yield (prop, source)


class TestPropertyExtractionSourcesRegistry:
    """Registry consistency and per-property source coverage."""

    def test_registry_uses_valid_sources(self):
        """Every source in the registry is a known extraction source."""
        for prop, sources in PROPERTY_EXTRACTION_SOURCES.items():
            for source in sources:
                assert source in ALL_SOURCES, (
                    f"Property {prop!r} lists unknown source {source!r}. "
                    f"Valid: {sorted(ALL_SOURCES)}"
                )

    def test_every_property_has_at_least_one_source(self):
        """Each property in the registry can be set by at least one source."""
        for prop, sources in PROPERTY_EXTRACTION_SOURCES.items():
            assert len(sources) >= 1, (
                f"Property {prop!r} has no extraction sources"
            )

    @pytest.mark.parametrize("property_name", list(PROPERTY_EXTRACTION_SOURCES.keys()))
    def test_property_flows_through_documented_sources(self, property_name):
        """Per-property: allowed sources are non-empty and valid."""
        sources = get_sources_for_property(property_name)
        assert len(sources) >= 1, (
            f"Property {property_name!r} should have at least one source"
        )
        for source in sources:
            assert source in ALL_SOURCES, (
                f"Property {property_name!r}: source {source!r} is not in ALL_SOURCES"
            )

    def test_adapter_recordings_are_in_registry(self):
        """Every (property, source) that adapters record is allowed by the registry."""
        registry_set = set(_registry_pairs())
        for prop, source in EXPECTED_ADAPTER_RECORDINGS:
            assert (prop, source) in registry_set, (
                f"Adapter records ({prop!r}, {source!r}) but registry does not allow it. "
                f"Allowed sources for {prop!r}: {get_sources_for_property(prop)}"
            )

    def test_registry_contains_all_adapter_recorded_properties(self):
        """Every property that any adapter records is in the registry."""
        recorded_props = {prop for prop, _ in EXPECTED_ADAPTER_RECORDINGS}
        registry_props = set(PROPERTY_EXTRACTION_SOURCES.keys())
        missing = recorded_props - registry_props
        assert not missing, (
            f"Properties recorded by adapters but missing from registry: {sorted(missing)}"
        )

    def test_every_source_that_can_set_property_is_hit(self):
        """For each property, every source that can set it is actually implemented (hit) by some adapter."""
        adapter_set = set(EXPECTED_ADAPTER_RECORDINGS)
        missing = []
        for prop, source in _registry_pairs():
            if (prop, source) not in adapter_set:
                missing.append((prop, source))
        assert not missing, (
            "Registry says these (property, source) pairs can set a property, "
            "but no adapter records them. Add the recording in the adapter and to EXPECTED_ADAPTER_RECORDINGS:\n  "
            + "\n  ".join(f"{p!r} <- {s!r}" for p, s in sorted(missing))
        )

    @pytest.mark.parametrize("property_name", list(PROPERTY_EXTRACTION_SOURCES.keys()))
    def test_property_every_source_is_hit(self, property_name):
        """Per-property: every source that can set this property is hit by some adapter."""
        adapter_set = set(EXPECTED_ADAPTER_RECORDINGS)
        allowed_sources = get_sources_for_property(property_name)
        unhit = [s for s in allowed_sources if (property_name, s) not in adapter_set]
        assert not unhit, (
            f"Property {property_name!r}: sources that can set it but are never recorded: {unhit}. "
            "Implement record() in the adapter and add to EXPECTED_ADAPTER_RECORDINGS."
        )


class TestGetSourcesForProperty:
    """API: get_sources_for_property / get_properties_for_source."""

    def test_unknown_property_returns_empty(self):
        assert get_sources_for_property("nonexistent_field") == ()

    def test_roundtrip(self):
        """For each property, get_sources_for_property and get_properties_for_source are consistent."""
        for prop, sources in PROPERTY_EXTRACTION_SOURCES.items():
            assert get_sources_for_property(prop) == sources
            for source in sources:
                assert prop in get_properties_for_source(source)
