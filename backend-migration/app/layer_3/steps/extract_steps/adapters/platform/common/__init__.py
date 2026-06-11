"""Common platform extraction steps and pipeline preamble."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.adapters.platform.common.platform_preamble_step import (
    CommonPlatformPreambleStep,
)


def common_platform_steps() -> tuple[ExtractionStep, ...]:
    """Return base platform steps shared across profiles (non-property setup only)."""
    return (CommonPlatformPreambleStep(),)


__all__ = [
    "CommonPlatformPreambleStep",
    "common_platform_steps",
]
