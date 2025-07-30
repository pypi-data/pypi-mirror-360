from pathlib import Path
from typing import Literal
from instaui.runtime._app import get_app_slot


_STATIC_DIR = Path(__file__).parent / "static"
_V3_JS = _STATIC_DIR / "tailwindcss-v3.min.js"
_V4_JS = _STATIC_DIR / "tailwindcss-v4.min.js"


def use_tailwind(value=True, *, version: Literal["v3", "v4"] = "v3"):
    """Enable or disable Tailwind CSS.

    Args:
        value (bool, optional): Whether to enable or disable Tailwind CSS. Defaults to True.
        version (Literal[&quot;v3&quot;, &quot;v4&quot;], optional): The version of Tailwind CSS to use. Defaults to "v3".
    """
    js_file = _V3_JS if version == "v3" else _V4_JS

    if value:
        get_app_slot()._html_resource.add_js_link(js_file)

    else:
        get_app_slot()._html_resource.remove_js_link(js_file)
