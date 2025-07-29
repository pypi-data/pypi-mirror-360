from pathlib import Path
from fastapi import APIRouter
from .loader import import_router_from_file
from .path_utils import path_from_dir
from .exceptions import DuplicateRouteError


def sort_key(p: Path) -> tuple[int, str]:
    n = p.name
    if n.startswith("["):
        return (1 if n.startswith("[...") else 2, n)
    return (0, n)


class RouterBuilder:
    def __init__(self, route_dir: Path):
        self.route_dir = route_dir
        self.path_to_route = {}
        self.reserved_path = {}

    def build(self) -> APIRouter:
        """
        Рекурсивно строит APIRouter и проверяет коллизии URL-шаблонов.
        """
        return self._build_router_tree(self.route_dir)

    def _build_router_tree(self, route_dir: Path) -> APIRouter:
        route_prefix = self.path_to_route.get(route_dir, '')

        files, route_path = [], None
        for p in route_dir.iterdir():
            if p.is_dir():
                files.append(p)
            elif (p.is_file()
                  and p.name.lower() == "route.py"
                  and route_path is None):
                route_path = p

        router = import_router_from_file(
            route_path) if route_path else APIRouter()

        for sub_dir in sorted(files, key=sort_key):
            local_prefix = path_from_dir(sub_dir.relative_to(route_dir))
            full_path = f'{route_prefix}{local_prefix}'
            self.path_to_route[sub_dir] = full_path

            if full_path in self.reserved_path:
                raise DuplicateRouteError(
                    self.reserved_path[full_path],
                    sub_dir / 'route.py',
                    full_path
                )
            self.reserved_path[full_path] = sub_dir / 'route.py'

            sub_router = self._build_router_tree(sub_dir)
            router.include_router(sub_router, prefix=local_prefix)

        return router
