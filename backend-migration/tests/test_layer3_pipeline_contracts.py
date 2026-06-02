from dataclasses import dataclass

import pytest

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.composers import PipelineComposer
from app.layer_3.steps.contracts import (
    ExtractionPipeline,
    ExtractionPipelineRunner,
    StepContext,
    StepState,
)
from app.layer_3.steps.extract_steps.services.files.citation import ExtractCitationTitleStep
from app.layer_3.steps.extract_steps.adapters.platform.common import CommonPlatformPreambleStep
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_repository_name_step import (
    ExtractGithubRepositoryNameStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_repository_name_step import (
    ExtractGitlabRepositoryNameStep,
)


@dataclass(frozen=True)
class _AppendStep(ExtractionStep):
    name: str
    token: str

    def run(self, context: StepContext, state: StepState) -> StepState:
        state.data.setdefault("order", []).append(self.token)
        return state


def test_pipeline_runner_executes_steps_in_order():
    pipeline = ExtractionPipeline(
        steps=(
            _AppendStep(name="first", token="a"),
            _AppendStep(name="second", token="b"),
        )
    )
    runner = ExtractionPipelineRunner()
    context = StepContext(repo_url="https://github.com/o/r", domain="software", schema="maSMP")
    state = StepState(metadata=SoftwareMetadata())

    result = runner.run(pipeline, context, state)

    assert result.data["order"] == ["a", "b"]


def test_pipeline_composer_software_returns_pipeline():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="maSMP", platform="github")
    assert isinstance(pipeline, ExtractionPipeline)
    assert len(pipeline.steps) > 0
    assert isinstance(pipeline.steps[0], CommonPlatformPreambleStep)
    assert isinstance(pipeline.steps[1], ExtractGithubRepositoryNameStep)
    assert any(isinstance(step, ExtractCitationTitleStep) for step in pipeline.steps)


def test_pipeline_composer_software_codemeta_returns_pipeline():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="codemeta", platform="gitlab")
    assert isinstance(pipeline, ExtractionPipeline)
    assert len(pipeline.steps) > 0
    assert isinstance(pipeline.steps[0], CommonPlatformPreambleStep)
    assert isinstance(pipeline.steps[1], ExtractGitlabRepositoryNameStep)
    assert any(isinstance(step, ExtractCitationTitleStep) for step in pipeline.steps)


def test_pipeline_platform_steps_populate_state():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="maSMP", platform="gitlab")
    runner = ExtractionPipelineRunner()
    context = StepContext(
        repo_url="https://gitlab.com/org/repo/",
        domain="software",
        schema="maSMP",
        platform="gitlab",
    )
    state = StepState(metadata=SoftwareMetadata(), data={"cff_content": "title: demo"})

    result = runner.run(pipeline, context, state)

    assert result.data["normalized_repo_url"] == "https://gitlab.com/org/repo"
    assert result.data["platform"] == "gitlab"


def test_pipeline_platform_file_discovery_differs_by_platform():
    composer = PipelineComposer()
    runner = ExtractionPipelineRunner()

    github_pipeline = composer.compose(domain="software", schema="maSMP", platform="github")
    github_result = runner.run(
        github_pipeline,
        StepContext(
            repo_url="https://github.com/org/repo",
            domain="software",
            schema="maSMP",
            platform="github",
        ),
        StepState(metadata=SoftwareMetadata(), data={"cff_content": "title: demo"}),
    )

    gitlab_pipeline = composer.compose(domain="software", schema="maSMP", platform="gitlab")
    gitlab_result = runner.run(
        gitlab_pipeline,
        StepContext(
            repo_url="https://gitlab.com/org/repo",
            domain="software",
            schema="maSMP",
            platform="gitlab",
        ),
        StepState(metadata=SoftwareMetadata(), data={"cff_content": "title: demo"}),
    )

    github_readme = github_result.data["metadata_file_candidates"]["readme"][0]
    gitlab_readme = gitlab_result.data["metadata_file_candidates"]["readme"][0]
    assert "/blob/" in github_readme
    assert "/-/blob/" in gitlab_readme


def test_pipeline_resolves_reachable_metadata_file_links():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="codemeta", platform="github")
    runner = ExtractionPipelineRunner()

    def _is_reachable(url: str) -> bool:
        return url.endswith("/blob/main/README.md") or url.endswith("/blob/master/CHANGELOG.md")

    result = runner.run(
        pipeline,
        StepContext(
            repo_url="https://github.com/org/repo",
            domain="software",
            schema="codemeta",
            platform="github",
        ),
        StepState(
            metadata=SoftwareMetadata(),
            data={"cff_content": "title: demo", "is_file_reachable_fn": _is_reachable},
        ),
    )

    assert result.metadata.codemeta_readme == "https://github.com/org/repo/blob/main/README.md"
    assert (
        result.metadata.masmp_changelog
        == "https://github.com/org/repo/blob/master/CHANGELOG.md"
    )


def test_pipeline_discovers_github_requirements_links_from_state_callbacks():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="maSMP", platform="github")
    runner = ExtractionPipelineRunner()

    def _list_contents(owner: str, repo: str, path: str):
        if path == "":
            return [{"type": "file", "name": "requirements.txt", "path": "requirements.txt"}]
        return []

    def _is_reachable(url: str) -> bool:
        return url.endswith("/blob/main/requirements.txt")

    result = runner.run(
        pipeline,
        StepContext(
            repo_url="https://github.com/org/repo",
            domain="software",
            schema="maSMP",
            platform="github",
        ),
        StepState(
            metadata=SoftwareMetadata(),
            data={
                "cff_content": "title: demo",
                "list_contents_fn": _list_contents,
                "is_file_reachable_fn": _is_reachable,
            },
        ),
    )

    assert result.metadata.softwareRequirements is not None
    assert result.metadata.softwareRequirements[0].endswith("/blob/main/requirements.txt")


def test_pipeline_discovers_gitlab_requirements_links_from_state_callbacks():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="codemeta", platform="gitlab")
    runner = ExtractionPipelineRunner()

    def _list_contents(owner: str, repo: str, path: str):
        if path == "":
            return [{"type": "blob", "name": "requirements.txt", "path": "requirements.txt"}]
        return []

    def _is_reachable(url: str) -> bool:
        return url.endswith("/-/blob/main/requirements.txt")

    result = runner.run(
        pipeline,
        StepContext(
            repo_url="https://gitlab.com/org/repo",
            domain="software",
            schema="codemeta",
            platform="gitlab",
        ),
        StepState(
            metadata=SoftwareMetadata(),
            data={
                "cff_content": "title: demo",
                "list_contents_fn": _list_contents,
                "is_file_reachable_fn": _is_reachable,
            },
        ),
    )

    assert result.metadata.softwareRequirements is not None
    assert result.metadata.softwareRequirements[0].endswith("/-/blob/main/requirements.txt")


def test_pipeline_composer_software_defaults_to_github_when_platform_missing():
    composer = PipelineComposer()
    pipeline = composer.compose(domain="software", schema="maSMP", platform=None)
    assert isinstance(pipeline, ExtractionPipeline)
    assert len(pipeline.steps) > 0


def test_pipeline_composer_software_unknown_platform_raises():
    composer = PipelineComposer()
    with pytest.raises(ValueError):
        composer.compose(domain="software", schema="codemeta", platform="bitbucket")


def test_pipeline_composer_software_unknown_schema_raises():
    composer = PipelineComposer()
    with pytest.raises(ValueError):
        composer.compose(domain="software", schema="schemaX", platform=None)


def test_pipeline_composer_unknown_domain_raises():
    composer = PipelineComposer()
    with pytest.raises(ValueError):
        composer.compose(domain="training", schema="X", platform=None)
