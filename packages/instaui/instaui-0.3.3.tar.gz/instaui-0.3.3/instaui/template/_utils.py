from __future__ import annotations
import typing
from pathlib import Path
from urllib.parse import quote
import base64


_JS_PREFIX = "data:text/javascript;charset=utf-8"
_CSS_PREFIX = "data:text/css;charset=utf-8"
_ICON_PREFIX = "data:image/x-icon;base64"


def normalize_path_to_dataurl(path: typing.Union[str, Path], prefix: str):
    if isinstance(path, Path):
        path = path.read_text(encoding="utf-8")

    return f"{prefix},{quote(path)}"


def normalize_path_to_base64_url(path: typing.Optional[Path], prefix: str):
    if path is None:
        return None
    return f"{prefix},{base64.b64encode(path.read_bytes()).decode('utf-8')}"
