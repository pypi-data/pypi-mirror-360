from pathlib import Path
from fastapi import APIRouter
from .builder import RouterBuilder


class FileRouter:
    def __init__(self, pages_dir: str = "pages"):
        self.pages_dir = Path(pages_dir).resolve()

    def build(self) -> APIRouter:
        builder = RouterBuilder(self.pages_dir)
        return builder.build()
