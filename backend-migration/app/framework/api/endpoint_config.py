"""Configuration for framework endpoint registration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointRegistrationConfig:
    """Controls which default endpoint groups are registered."""

    include_metadata: bool = True
    include_debug: bool = True
    include_system: bool = True
