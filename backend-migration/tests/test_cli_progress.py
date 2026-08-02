"""Tests for terminal progress rendering without a terminal dependency."""
from __future__ import annotations

from io import StringIO

from app.cli import TerminalProgress


def test_terminal_progress_renders_pipeline_and_completion():
    stream = StringIO()
    progress = TerminalProgress(enabled=True, stream=stream)

    progress.callback("pipeline", "started")
    progress.callback("pipeline", "completed")
    progress.callback("jsonld_build", "started")
    progress.callback("jsonld_build", "completed")

    rendered = stream.getvalue()
    assert "Extracting repository metadata" in rendered
    assert "Building JSON-LD result" in rendered
    assert "100%" in rendered
    assert rendered.endswith("\n")


def test_terminal_progress_is_silent_when_disabled():
    stream = StringIO()
    progress = TerminalProgress(enabled=False, stream=stream)

    progress.callback("pipeline", "completed")

    assert stream.getvalue() == ""


def test_terminal_progress_shows_each_pipeline_step_and_position():
    stream = StringIO()
    progress = TerminalProgress(enabled=True, stream=stream)

    progress.step_callback("gitlab.extract_contributors", 2, 5, "started")
    progress.step_callback("gitlab.extract_contributors", 2, 5, "completed")

    rendered = stream.getvalue()
    assert "Running: gitlab · extract contributors" in rendered
    assert "(1/6)" in rendered
    assert "(2/6)" in rendered
