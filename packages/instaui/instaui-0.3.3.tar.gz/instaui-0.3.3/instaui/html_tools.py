from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union
from instaui.common.jsonable import dumps, dumps2dict
from instaui.runtime._app import get_app_slot
from instaui.tailwind._index import use_tailwind

use_tailwind = use_tailwind


def add_css_link(href: Union[str, Path]):
    """Add a link to a CSS file to the HTML document.

    Args:
        href (Union[str, Path]): The path to the CSS file.
    """
    get_app_slot()._html_resource.add_css_link(href)


def remove_css_link(href: Union[str, Path]):
    """Remove a link to a CSS file from the HTML document.

    Args:
        href (Union[str, Path]): The path to the CSS file.
    """
    get_app_slot()._html_resource.remove_css_link(href)


def add_js_link(
    link: Union[str, Path],
    *,
    type: Optional[Literal["module"]] = None,
):
    """Add a link to a JavaScript file to the HTML document.

    Args:
        link (Union[str, Path]): The path to the JavaScript file.
        type (Optional[Literal[&quot;module&quot;]], optional): The type of the JavaScript file. Defaults to None.
    """

    attrs = {
        "type": type,
    }

    get_app_slot()._html_resource.add_js_link(link, attrs=attrs)


add_style = get_app_slot()._html_resource.add_style_tag


def use_page_title(title: str):
    """Set the title of the HTML document.

    Args:
        title (str): The title of the HTML document.
    """
    get_app_slot()._html_resource.title = title


def use_favicon(favicon: Path):
    """Set the favicon of the HTML document.

    Args:
        favicon (Path): The path to the favicon.
    """
    get_app_slot()._html_resource.favicon = favicon


def add_js_code(code: str, *, script_attrs: Optional[Dict[str, Any]] = None):
    """Add a script tag to the HTML document with the given JavaScript code.

    Args:
        code (str): The JavaScript code.
        script_attrs (Optional[Dict[str, Any]], optional): The attributes of the script tag. Defaults to None.
    """
    get_app_slot()._html_resource.add_script_tag(code, script_attrs=script_attrs)


def add_vue_app_use(name: str):
    get_app_slot()._html_resource.add_vue_app_use(name)


def to_config_data() -> Dict:
    app = get_app_slot()
    data = dumps2dict(app)

    # Exclude scopes that contain only the id field.
    scopes = [s for s in dumps2dict(app._scopes) if len(s) > 1]
    data["scopes"] = scopes
    return data


def to_json(indent=False):
    return dumps(to_config_data(), indent=indent)
