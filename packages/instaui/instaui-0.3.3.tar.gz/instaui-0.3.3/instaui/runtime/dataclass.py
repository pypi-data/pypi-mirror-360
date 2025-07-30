from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Union
from dataclasses import dataclass, field


@dataclass
class JsLink:
    link: Union[str, Path]
    attrs: Dict[str, Any] = field(default_factory=dict)

    def create_attrs_str(self):
        return " ".join(f'{k}="{v}"' for k, v in self.attrs.items() if v is not None)


@dataclass(frozen=True)
class VueAppUse:
    name: str


@dataclass(frozen=True)
class VueAppComponent:
    name: str
    url: str


@dataclass
class ImportMaps:
    name: str
    url: str
