"""
Shared primitives (Person, License, …) reused across domain models.

Concrete definitions live in `types.py`.
"""

from app.layer_1.entities.shared_primitives.types import (
    License,
    Person,
    ReferencePublication,
    VersionControlSystem,
)

__all__ = [
    "License",
    "Person",
    "ReferencePublication",
    "VersionControlSystem",
]
