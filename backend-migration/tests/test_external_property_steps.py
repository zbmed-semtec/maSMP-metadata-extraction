"""Tests for external source-property steps and property-level merge."""

from typing import Any, Dict, Optional

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import ExtractionPipeline, ExtractionPipelineRunner, StepContext, StepState
from app.layer_3.steps.extract_steps.services.external.openalex import (
    ExtractOpenAlexAuthorsStep,
    ExtractOpenAlexKeywordsStep,
    ExtractOpenAlexReferencePublicationStep,
)
from app.layer_3.steps.extract_steps.services.external.software_heritage import (
    ExtractSoftwareHeritageArchivedUrlStep,
)
from app.layer_3.steps.extract_steps.services.external.wayback import ExtractWaybackArchivedUrlStep
from app.layer_3.steps.extract_steps.services.external.zenodo import ExtractZenodoArchivedUrlsStep
from app.layer_3.steps.merge_steps.software import (
    MergeSoftwareArchivedUrlsStep,
    MergeSoftwareAuthorsStep,
    MergeSoftwareKeywordsStep,
    MergeSoftwareReferencePublicationStep,
)


class DummyOpenAlexClient:
    """Only implements HTTP-style fetch; property steps own extraction logic."""

    def __init__(self, work: Dict[str, Any] | None):
        self.work = work

    def fetch_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        return self.work


class DummyWaybackClient:
    def check_software_heritage(self, url: str) -> str:
        return "https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/org/repo"

    def check_archive_url(self, url: str) -> str:
        return "https://web.archive.org/web/https://github.com/org/repo"


def test_external_archive_steps_merge_archived_urls():
    state = StepState(
        metadata=SoftwareMetadata(),
        data={"readme_content": "https://zenodo.org/record/111111"},
    )
    context = StepContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="CODEMETA",
        platform="github",
    )
    dummy = DummyWaybackClient()
    pipeline = ExtractionPipeline(
        steps=(
            ExtractZenodoArchivedUrlsStep(),
            ExtractSoftwareHeritageArchivedUrlStep(lookup_fn=dummy.check_software_heritage),
            ExtractWaybackArchivedUrlStep(dummy),
            MergeSoftwareArchivedUrlsStep(),
        )
    )

    result = ExtractionPipelineRunner().run(pipeline, context, state)

    assert result.metadata.archivedAt is not None
    assert len(result.metadata.archivedAt) == 3


def test_openalex_property_steps_merge_metadata():
    work = {
        "title": "OpenAlex Work",
        "keywords": ["from-openalex"],
        "authorships": [{"author": {"display_name": "Jane Doe"}}],
    }
    client = DummyOpenAlexClient(work)
    state = StepState(
        metadata=SoftwareMetadata(identifier=["https://doi.org/10.1234/abcd"]),
        data={},
    )
    context = StepContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="CODEMETA",
        platform="github",
    )
    pipeline = ExtractionPipeline(
        steps=(
            ExtractOpenAlexKeywordsStep(client),
            MergeSoftwareKeywordsStep(),
            ExtractOpenAlexAuthorsStep(client),
            MergeSoftwareAuthorsStep(),
            ExtractOpenAlexReferencePublicationStep(client),
            MergeSoftwareReferencePublicationStep(),
        )
    )

    result = ExtractionPipelineRunner().run(pipeline, context, state)

    assert "from-openalex" in (result.metadata.keywords or [])
    assert result.metadata.author and result.metadata.author[0]["familyName"] == "Doe"
    assert result.metadata.codemeta_referencePublication is not None
    assert result.metadata.codemeta_referencePublication.name == "OpenAlex Work"

