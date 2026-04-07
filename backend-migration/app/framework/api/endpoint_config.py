"""Configuration for framework endpoint registration."""

from dataclasses import dataclass
import os


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class EndpointRegistrationConfig:
    """Controls which default endpoint groups are registered."""

    include_metadata: bool = True
    include_debug: bool = True
    include_system: bool = True

    @classmethod
    def from_env(cls) -> "EndpointRegistrationConfig":
        """Create endpoint registration config from environment variables."""
        return cls(
            include_metadata=_env_bool("COMET_RS_INCLUDE_METADATA_ENDPOINTS", True),
            include_debug=_env_bool("COMET_RS_INCLUDE_DEBUG_ENDPOINTS", True),
            include_system=_env_bool("COMET_RS_INCLUDE_SYSTEM_ENDPOINTS", True),
        )
