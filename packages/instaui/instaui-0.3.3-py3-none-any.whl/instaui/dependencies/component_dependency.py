from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set

_TTagName = str


@dataclass(frozen=True)
class ComponentDependencyInfo:
    tag_name: _TTagName = field(hash=True)
    esm: Path = field(hash=False)
    externals: Dict[str, Path] = field(default_factory=dict, compare=False, hash=False)
    css: Set[Path] = field(default_factory=set, compare=False, hash=False)

    def copy(self):
        return ComponentDependencyInfo(
            tag_name=self.tag_name,
            esm=self.esm,
            externals={**self.externals},
            css=set(self.css),
        )
