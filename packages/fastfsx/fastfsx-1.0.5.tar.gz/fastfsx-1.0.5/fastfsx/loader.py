import importlib.util
from pathlib import Path
import sys
from fastapi import APIRouter
from .exceptions import InvalidRouterError


def import_router_from_file(route_file: Path) -> APIRouter:
    module_name = "_fastfsx_routes_" + \
        "_".join(route_file.with_suffix("").parts)
    if module_name in sys.modules:
        return getattr(sys.modules[module_name], "router")

    spec = importlib.util.spec_from_file_location(module_name, route_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    router = getattr(module, "router", None)
    if not isinstance(router, APIRouter):
        raise InvalidRouterError(route_file)
    return router
