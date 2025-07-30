from __future__ import annotations
import typing
from dataclasses import dataclass, field
from .env import env
from instaui.common.jsonable import dumps
from instaui.runtime.context import get_context
from instaui.runtime.dataclass import JsLink, VueAppComponent


if typing.TYPE_CHECKING:
    from instaui.runtime.resource import StyleTag


_html_template = env.get_template("web.html")


@dataclass
class WebTemplateModel:
    version: str
    vue_js_link: str
    instaui_js_link: str
    config_dict: typing.Dict[str, typing.Any] = field(default_factory=dict)
    extra_import_maps: typing.Dict[str, str] = field(default_factory=dict)
    css_links: typing.List[str] = field(default_factory=list)
    style_tags: typing.List[StyleTag] = field(default_factory=list)
    js_links: typing.List[JsLink] = field(default_factory=list)
    script_tags: typing.List[str] = field(default_factory=list)
    vue_app_use: typing.List[str] = field(default_factory=list)
    vue_app_component: typing.List[VueAppComponent] = field(default_factory=list)
    prefix: str = ""
    title: typing.Optional[str] = None
    favicon_url: str = ""

    def add_extra_import_map(self, name: str, url: str):
        self.extra_import_maps[name] = url

    @property
    def import_maps_string(self):
        data = {
            **self.extra_import_maps,
            "vue": self.vue_js_link,
            "instaui": self.instaui_js_link,
        }

        return dumps(data)

    @property
    def is_debug(self):
        context = get_context()
        return context.debug_mode


def render_web_html(model: WebTemplateModel):
    return _html_template.render(model=model)
