from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.framework.api.endpoint_config import EndpointRegistrationConfig
from app.framework.api.endpoint_registry import register_default_endpoints


def _route_paths(app: FastAPI) -> set[str]:
    return {
        route.path
        for route in app.routes
        if isinstance(route, APIRoute)
    }


def test_register_default_endpoints_includes_all_by_default():
    app = FastAPI()
    register_default_endpoints(app)
    paths = _route_paths(app)
    assert "/api/metadata" in paths
    assert "/api/debug/pipeline-parity" in paths
    assert "/api/health" in paths


def test_register_default_endpoints_can_exclude_debug_and_system():
    app = FastAPI()
    register_default_endpoints(
        app,
        config=EndpointRegistrationConfig(
            include_metadata=True,
            include_debug=False,
            include_system=False,
        ),
    )
    paths = _route_paths(app)
    assert "/api/metadata" in paths
    assert "/api/debug/pipeline-parity" not in paths
    assert "/api/health" not in paths
