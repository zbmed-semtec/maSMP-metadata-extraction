"""Default software extraction profile.

Backward-compatible alias for maSMP software profile.
"""
from __future__ import annotations

from app.layer_3.composers.profiles.software_masmp import build_software_masmp_pipeline
from app.layer_3.steps.contracts.pipeline import ExtractionPipeline


def build_software_default_pipeline() -> ExtractionPipeline:
    """
    Return the default software extraction pipeline.

    Keep this alias while call sites migrate to explicit schema profiles.
    """
    return build_software_masmp_pipeline()
