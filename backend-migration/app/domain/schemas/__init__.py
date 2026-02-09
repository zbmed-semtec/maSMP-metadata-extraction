"""Domain schema definitions (e.g. maSMP profile categories)."""
from app.domain.schemas.masmp_profiles import (
    PROFILE_CATEGORIES,
    get_category_for_key,
)

__all__ = ["PROFILE_CATEGORIES", "get_category_for_key"]
