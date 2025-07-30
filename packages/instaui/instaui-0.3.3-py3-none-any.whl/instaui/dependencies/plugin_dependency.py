from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from instaui.runtime._app import get_app_slot


@dataclass(frozen=True)
class PluginDependencyInfo:
    name: str = field(hash=True)
    esm: Path = field(hash=False)
    externals: Optional[List[Path]] = field(
        default_factory=list, compare=False, hash=False
    )
    css: List[Path] = field(default_factory=list, compare=False, hash=False)


def register_plugin(
    name: str,
    esm: Path,
    *,
    externals: Optional[List[Path]] = None,
    css: Optional[List[Path]] = None,
):
    info = PluginDependencyInfo(f"plugin/{name}", esm, externals or [], css or [])

    get_app_slot().use_plugin_dependency(info)
    return info
