from pathlib import Path


class InvalidRouterError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"`router` not found or invalid in {path}")


class DuplicateRouteError(RuntimeError):
    """
    Поднимается, если два разных `route.py` описывают одинаковый HTTP‑шаблон.

    Parameters
    ----------
    path_a : Path
        Первый файл‑источник маршрута.
    path_b : Path
        Второй файл‑источник маршрута (конфликтующий).
    endpoint : str
        Итоговый URL‑шаблон (пример: "/admin/athlete/{id}").
    """

    def __init__(self, path_a: Path, path_b: Path, endpoint: str) -> None:
        self.path_a: Path = path_a
        self.path_b: Path = path_b
        self.endpoint: str = endpoint
        super().__init__(self._make_message())

    def _make_message(self) -> str:
        return (
            "Duplicate route detected:\n"
            f"  • {self.endpoint!r} is defined in\n"
            f"    ├─ {self.path_a}\n"
            f"    └─ {self.path_b}\n"
            "Resolve the conflict by renaming or removing one of the files."
        )

    def __str__(self) -> str:
        return self._make_message()
