from dataclasses import dataclass
import itertools
from pathlib import Path
import shutil
from typing import Callable, Optional
from urllib.parse import quote

from instaui.version import __version__ as _INSTAUI_VERSION
from instaui.html_tools import to_config_data
from instaui.runtime._app import get_app_slot, get_default_app_slot
from instaui.systems import file_system
from instaui.template import webview_template
from instaui import consts
from instaui.runtime.resource import StyleTag
from . import _utils


_INDEX_HTML_NAME = "index.html"


@dataclass
class ResourceInfo:
    title: str
    index_html_url: str


def resource_to_assets(
    page_url: str, assets_path: Path, on_app_mounted: Optional[Callable] = None
):
    page_dir = assets_path.joinpath(quote(page_url, safe=""))
    _utils.reset_dir(page_dir)

    relative_to_assets = _get_relative_to_assets(page_dir)
    file_to_assets = _get_file_to_assets(page_dir)

    config_data = to_config_data()

    system_slot = get_app_slot()
    default_app_slot = get_default_app_slot()
    html_resource = system_slot._html_resource
    default_html_resource = default_app_slot._html_resource

    if html_resource.favicon:
        favicon_url = file_to_assets(html_resource.favicon)
    else:
        if default_html_resource.favicon:
            favicon_url = file_to_assets(default_html_resource.favicon)
        else:
            favicon_url = file_to_assets(consts.FAVICON_PATH)

    model = webview_template.WebViewTemplateModel(
        version=_INSTAUI_VERSION,
        vue_js_code=file_to_assets(consts.VUE_ES_JS_PATH),
        instaui_js_code=file_to_assets(consts.APP_ES_JS_PATH),
        css_links=[
            file_to_assets(consts.APP_CSS_PATH),
        ],
        config_dict=config_data,
        favicon_url=favicon_url,
        title=html_resource.title or default_html_resource.title or consts.PAGE_TITLE,
        on_app_mounted=on_app_mounted,
    )

    # register custom components
    for component in system_slot._component_dependencies:
        if not component.esm:
            continue

        component_url = file_to_assets(component.esm)
        model.add_extra_import_map(component_url, file_to_assets(component.esm))

        model.vue_app_component.append(
            webview_template.WebViewVueAppComponent(
                name=component.tag_name,
                url=component_url,
            )
        )

        if component.css:
            for css_link in component.css:
                css_resource = file_to_assets(css_link)
                if css_link.is_file():
                    model.css_links.append(css_resource)

        if component.externals:
            for name, file in component.externals.items():
                model.add_extra_import_map(name, file_to_assets(file))

    # register custom plugins
    for plugin in set(
        itertools.chain(
            system_slot._plugin_dependencies, default_app_slot._plugin_dependencies
        )
    ):
        if not plugin.esm:
            continue

        model.vue_app_use.append(plugin.name)

        model.add_extra_import_map(plugin.name, file_to_assets(plugin.esm))

        if plugin.css:
            for css_link in plugin.css:
                model.css_links.append(file_to_assets(css_link))

    # css file link to web static link
    for link in html_resource.get_valid_css_links(
        default_html_resource._css_links_manager
    ):
        if isinstance(link, Path):
            model.css_links.append(file_to_assets(link))
        else:
            model.css_links.append(link)

    # js file link to web static link
    for info in html_resource.get_valid_js_links(
        default_html_resource._js_links_manager
    ):
        link = file_to_assets(info.link) if isinstance(info.link, Path) else info.link
        model.js_links.append(link)

    for js_code in itertools.chain(
        html_resource._script_tags, default_html_resource._script_tags
    ):
        model.script_tags.append(js_code)

    for sylte_tag in StyleTag.merge_by_group_id(
        itertools.chain(html_resource._style_tags, default_html_resource._style_tags)
    ):
        model.style_tags.append(sylte_tag)

    html_str = webview_template.render_wbeview_html(model)

    index_html_path = page_dir / _INDEX_HTML_NAME
    index_html_path.write_text(html_str, encoding="utf-8")
    relative_to_assets(index_html_path)
    index_html_url = str(index_html_path.absolute())
    return ResourceInfo(
        title="test",
        index_html_url=index_html_url,
    )


def _get_relative_to_assets(assets_path: Path):
    def wrapper(file_path: Path, relative_parent=False):
        return str(
            file_path.relative_to(
                assets_path.parent if relative_parent else assets_path
            )
        ).replace("\\", "/")

    return wrapper


def _get_file_to_assets(assets_path: Path):
    relative_to_assets = _get_relative_to_assets(assets_path)

    def wrapper(file_path: Path):
        hash_part = file_system.generate_hash_name_from_path(file_path.parent)
        new_folder_path = assets_path.joinpath(hash_part)

        if not new_folder_path.exists():
            new_folder_path.mkdir(parents=True)

        new_path = new_folder_path.joinpath(file_path.name)

        if file_path.is_file():
            shutil.copyfile(file_path, new_path)
            return "./" + relative_to_assets(new_path)
        else:
            shutil.copytree(file_path, new_path, dirs_exist_ok=True)
            return "./" + relative_to_assets(new_path) + "/"

    return wrapper
