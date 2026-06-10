"""
Research-software aggregate: import `SoftwareMetadata` from this package.

Implementation: `metadata.py`. `RepositoryMetadata` is a backward-compatible alias.
"""

from app.layer_1.entities.software_metadata.metadata import RepositoryMetadata, SoftwareMetadata

__all__ = ["RepositoryMetadata", "SoftwareMetadata"]
