"""Pick first reachable URL from candidate lists (README / CHANGELOG)."""
from __future__ import annotations

from app.layer_3.steps.extract_steps.adapters.platform.common.helpers.metadata_link_candidates import (
    first_reachable_url,
)

__all__ = ["first_reachable_url"]
