from __future__ import annotations
import typing
from dataclasses import dataclass, field
from instaui.common.jsonable import dumps
from .env import env

if typing.TYPE_CHECKING:
    from instaui.runtime.resource import StyleTag


_html_template = env.get_template("webview.html")


@dataclass(frozen=True)
class WebViewVueAppComponent:
    name: str
    url: str


@dataclass
class WebViewTemplateModel:
    version: str
    vue_js_code: str
    instaui_js_code: str
    config_dict: typing.Dict[str, typing.Any] = field(default_factory=dict)
    extra_import_maps: typing.Dict[str, str] = field(default_factory=dict)
    css_links: typing.List[str] = field(default_factory=list)
    style_tags: typing.List[StyleTag] = field(default_factory=list)
    js_links: typing.List[str] = field(default_factory=list)
    script_tags: typing.List[str] = field(default_factory=list)
    vue_app_use: typing.List[str] = field(default_factory=list)
    vue_app_component: typing.List[WebViewVueAppComponent] = field(default_factory=list)
    title: typing.Optional[str] = None
    favicon_url: typing.Optional[str] = None
    on_app_mounted: typing.Optional[typing.Callable] = None

    def add_extra_import_map(self, name: str, code: str):
        self.extra_import_maps[name] = code

    @property
    def import_maps_string(self):
        data = {
            **self.extra_import_maps,
            "vue": self.vue_js_code,
            "instaui": self.instaui_js_code,
        }

        return dumps(data)


def render_wbeview_html(model: WebViewTemplateModel) -> str:
    return _html_template.render(model=model)
