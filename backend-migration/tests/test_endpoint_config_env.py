from app.framework.api.endpoint_config import EndpointRegistrationConfig


def test_endpoint_registration_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("COMET_RS_INCLUDE_METADATA_ENDPOINTS", raising=False)
    monkeypatch.delenv("COMET_RS_INCLUDE_DEBUG_ENDPOINTS", raising=False)
    monkeypatch.delenv("COMET_RS_INCLUDE_SYSTEM_ENDPOINTS", raising=False)

    config = EndpointRegistrationConfig.from_env()
    assert config.include_metadata is True
    assert config.include_debug is True
    assert config.include_system is True


def test_endpoint_registration_config_from_env_overrides(monkeypatch):
    monkeypatch.setenv("COMET_RS_INCLUDE_METADATA_ENDPOINTS", "true")
    monkeypatch.setenv("COMET_RS_INCLUDE_DEBUG_ENDPOINTS", "0")
    monkeypatch.setenv("COMET_RS_INCLUDE_SYSTEM_ENDPOINTS", "no")

    config = EndpointRegistrationConfig.from_env()
    assert config.include_metadata is True
    assert config.include_debug is False
    assert config.include_system is False
