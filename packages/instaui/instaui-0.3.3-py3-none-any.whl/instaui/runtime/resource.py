from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Union
from .dataclass import JsLink, VueAppUse, VueAppComponent
from ._link_manager import LinkManager
from itertools import groupby


class HtmlResource:
    use_tailwind: Optional[bool] = None
    title: Optional[str] = None
    favicon: Optional[Path] = None

    def __init__(self) -> None:
        self._css_links_manager: LinkManager[Union[str, Path]] = LinkManager()
        self._style_tags: List[StyleTag] = []
        self._js_links_manager: LinkManager[JsLink] = LinkManager(
            key_fn=lambda js_link: js_link.link
        )
        self._script_tags: List[str] = []
        self._vue_app_use: Set[VueAppUse] = set()
        self._vue_app_components: Set[VueAppComponent] = set()
        self._import_maps: Dict[str, str] = {}
        self._appConfig = "{}"

    def add_css_link(self, link: Union[str, Path]):
        self._css_links_manager.add_link(link)

    def remove_css_link(self, link: Union[str, Path]):
        self._css_links_manager.remove_link(link)

    def add_style_tag(self, content: str, *, group_id: Optional[str] = None):
        """Add a style tag to the HTML document.

        Args:
            content (str): The content of the style tag.
            group_id (Optional[str], optional): The group id of the style tag. Defaults to None.
        """
        self._style_tags.append(StyleTag(content, group_id))

    def add_js_link(
        self,
        link: Union[str, Path],
        *,
        attrs: Optional[Dict[str, Any]] = None,
    ):
        self._js_links_manager.add_link(JsLink(link, attrs or {}))

    def remove_js_link(self, link: Union[str, Path]):
        self._js_links_manager.remove_link(JsLink(link))

    def get_valid_js_links(self, default_js_links_manager: LinkManager) -> List[JsLink]:
        return self._js_links_manager.get_valid_links(default_js_links_manager)

    def get_valid_css_links(
        self, default_css_links_manager: LinkManager[Union[str, Path]]
    ) -> List[Union[str, Path]]:
        return self._css_links_manager.get_valid_links(default_css_links_manager)

    def add_script_tag(
        self, content: str, script_attrs: Optional[Dict[str, Any]] = None
    ):
        self._script_tags.append(content)

    def add_vue_app_use(self, name: str):
        self._vue_app_use.add(VueAppUse(name))

    def add_vue_app_component(self, name: str, url: str):
        self._vue_app_components.add(VueAppComponent(name, url))

    def add_import_map(self, name: str, link: str):
        self._import_maps[name] = link


@dataclass(frozen=True)
class StyleTag:
    content: str
    group_id: Optional[str] = None

    @staticmethod
    def merge_by_group_id(tags: Iterable[StyleTag]) -> Iterable[StyleTag]:
        sorted_tags = sorted(tags, key=lambda tag: tag.group_id or "")
        for group_id, group_tags in groupby(sorted_tags, lambda tag: tag.group_id):
            yield StyleTag(
                "\n".join(tag.content for tag in group_tags), group_id=group_id
            )
