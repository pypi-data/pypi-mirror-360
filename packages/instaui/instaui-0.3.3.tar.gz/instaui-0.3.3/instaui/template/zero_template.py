from __future__ import annotations
import typing
from pathlib import Path
from urllib.parse import quote
import base64
from dataclasses import dataclass, field
from .env import env
from instaui.common.jsonable import dumps
from instaui.runtime.dataclass import JsLink

if typing.TYPE_CHECKING:
    from instaui.runtime.resource import StyleTag


_TCodeOrPath = typing.Union[str, Path]
_JS_PREFIX = "data:text/javascript;charset=utf-8"
_CSS_PREFIX = "data:text/css;charset=utf-8"
_ICON_PREFIX = "data:image/x-icon;base64"

_html_template = env.get_template("zero.html")


@dataclass(frozen=True)
class ZeroVueAppComponent:
    name: str
    url: _TCodeOrPath


@dataclass
class ZeroTemplateModel:
    version: str
    vue_js_code: _TCodeOrPath
    instaui_js_code: _TCodeOrPath
    config_dict: typing.Dict[str, typing.Any] = field(default_factory=dict)
    extra_import_maps: typing.Dict[str, _TCodeOrPath] = field(default_factory=dict)
    css_links: typing.List[_TCodeOrPath] = field(default_factory=list)
    style_tags: typing.List[StyleTag] = field(default_factory=list)
    js_links: typing.List[JsLink] = field(default_factory=list)
    script_tags: typing.List[str] = field(default_factory=list)
    vue_app_use: typing.List[str] = field(default_factory=list)
    vue_app_component: typing.List[ZeroVueAppComponent] = field(default_factory=list)
    prefix: str = ""
    title: typing.Optional[str] = None
    favicon: typing.Optional[Path] = None

    def add_extra_import_map(self, name: str, url: _TCodeOrPath):
        self.extra_import_maps[name] = url

    @property
    def import_maps_string(self):
        data = {
            **self.extra_import_maps,
            "vue": self.vue_js_code,
            "instaui": self.instaui_js_code,
        }

        return dumps(data)

    def normalize_path_with_self(self):
        self.vue_js_code = _normalize_path_to_dataurl(self.vue_js_code, _JS_PREFIX)
        self.instaui_js_code = _normalize_path_to_dataurl(
            self.instaui_js_code, _JS_PREFIX
        )

        self.css_links = [
            _normalize_path_to_dataurl(link, _CSS_PREFIX)
            for link in self.css_links
            if isinstance(link, str) or (isinstance(link, Path) and link.is_file())
        ]

        self.js_links = [
            JsLink(
                link=_normalize_path_to_dataurl(link.link, _JS_PREFIX),
                attrs=link.attrs,
            )
            for link in self.js_links
        ]

        self.extra_import_maps = {
            k: _normalize_path_to_dataurl(v, _JS_PREFIX)
            for k, v in self.extra_import_maps.items()
        }

        self.vue_app_component = [
            ZeroVueAppComponent(
                name=component.name,
                url=_normalize_path_to_dataurl(component.url, _JS_PREFIX),
            )
            for component in self.vue_app_component
        ]

        self.favicon = _normalize_path_to_base64_url(self.favicon, _ICON_PREFIX)  # type: ignore


def _normalize_path_to_dataurl(path: typing.Union[str, Path], prefix: str):
    if isinstance(path, Path):
        path = path.read_text(encoding="utf-8")

    return f"{prefix},{quote(path)}"


def _normalize_path_to_base64_url(path: typing.Optional[Path], prefix: str):
    if path is None:
        return None
    return f"{prefix},{base64.b64encode(path.read_bytes()).decode('utf-8')}"


def render_zero_html(model: ZeroTemplateModel) -> str:
    model.normalize_path_with_self()
    return _html_template.render(model=model)
