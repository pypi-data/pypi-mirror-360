from __future__ import annotations
from typing import Callable
from dataclasses import dataclass
from urllib.parse import quote


@dataclass
class PageInfo:
    path: str
    func: Callable

    def create_key(self) -> str:
        return quote(self.path)
