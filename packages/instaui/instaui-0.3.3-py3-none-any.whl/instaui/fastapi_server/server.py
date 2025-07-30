from __future__ import annotations
from contextlib import contextmanager
import inspect
import os
import multiprocessing
from pathlib import Path
from typing import Any, Optional, Set, Union
import __main__

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from uvicorn.supervisors import ChangeReload
import itertools

from instaui.html_tools import to_config_data
from instaui.launch_collector import get_launch_collector
from instaui.page_info import PageInfo

from instaui import consts
from instaui.runtime._app import get_app_slot, get_default_app_slot
from instaui.runtime.context import get_context
from instaui.runtime.dataclass import JsLink, VueAppComponent
from instaui.template import web_template
from instaui.runtime.resource import StyleTag


from . import dependency_router
from . import event_router
from . import watch_router
from . import debug_mode_router
from .middlewares import RequestContextMiddleware, NoCacheDebugModeMiddleware
from ._uvicorn import UvicornServer
from . import resource
from instaui.version import __version__ as _INSTA_VERSION

APP_IMPORT_STRING = "instaui.fastapi_server.server:Server._instance.app"


INSTAUI_STATIC_URL = f"/_instaui_{_INSTA_VERSION}/static"


def _cal_static_link(target_path: Path):
    return f"{INSTAUI_STATIC_URL}/{target_path.relative_to(consts._STATIC_DIR)}"


VUE_JS_HASH_LINK = _cal_static_link(consts.VUE_ES_JS_PATH)
INSTAUI_JS_HASH_LINK = _cal_static_link(consts.APP_ES_JS_PATH)
APP_CSS_LINK = _cal_static_link(consts.APP_CSS_PATH)
FAVICON_LINK = _cal_static_link(consts.FAVICON_PATH)


class Server:
    _instance: Optional[Server] = None

    def __init__(
        self,
        use_gzip: Union[int, bool] = True,
    ):
        self.app = FastAPI()
        self.app.add_middleware(RequestContextMiddleware)
        if get_context().debug_mode:
            self.app.add_middleware(NoCacheDebugModeMiddleware)

        if use_gzip:
            self.app.add_middleware(
                GZipMiddleware,
                minimum_size=use_gzip if isinstance(use_gzip, int) else 500,
            )

        dependency_router.create_router(self.app)
        event_router.create_router(self.app)
        watch_router.create_router(self.app)
        debug_mode_router.create_router(self.app)

        self.add_instaui_static(self.app)

        for page_info in get_launch_collector()._page_router.values():
            self.register_page(page_info)

        self._registered_static_routes: Set[str] = set()

        Server._instance = self

    def register_page(self, info: PageInfo):
        is_async = inspect.iscoroutinefunction(info.func)

        self._remove_route(info.path)

        if is_async:

            @self.app.get(info.path)
            async def _(request: Request):
                self._update_page_info(request, info)
                with _execute_request_lifespans():
                    await info.func()
                html = self._to_web_html(
                    page_info=info,
                    request=request,
                )

                return HTMLResponse(html)

        else:

            @self.app.get(info.path)
            def _(request: Request):
                self._update_page_info(request, info)
                with _execute_request_lifespans():
                    info.func()
                html = self._to_web_html(
                    page_info=info,
                    request=request,
                )

                return HTMLResponse(html)

    def _to_web_html(
        self,
        *,
        page_info: PageInfo,
        request: Request,
    ):
        config_data = to_config_data()

        system_slot = get_app_slot()
        default_app_slot = get_default_app_slot()
        html_resource = system_slot._html_resource
        default_html_resource = default_app_slot._html_resource

        favicon_url = FAVICON_LINK
        if html_resource.favicon:
            favicon_url = resource.record_resource(html_resource.favicon)
        else:
            if default_html_resource.favicon:
                favicon_url = resource.record_resource(default_html_resource.favicon)

        model = web_template.WebTemplateModel(
            version=_INSTA_VERSION,
            vue_js_link=VUE_JS_HASH_LINK,
            instaui_js_link=INSTAUI_JS_HASH_LINK,
            css_links=[
                APP_CSS_LINK,
            ],
            config_dict=config_data,
            favicon_url=favicon_url,
            title=html_resource.title
            or default_html_resource.title
            or consts.PAGE_TITLE,
        )

        # register custom components
        for component in system_slot._component_dependencies:
            if not component.esm:
                continue

            model.vue_app_component.append(
                VueAppComponent(
                    name=component.tag_name,
                    url=resource.record_resource(component.esm),
                )
            )

            if component.css:
                for css_link in component.css:
                    css_resource = resource.record_resource(css_link)
                    if css_link.is_file():
                        model.css_links.append(css_resource)

            if component.externals:
                for name, url in component.externals.items():
                    model.add_extra_import_map(name, resource.record_resource(url))

        # register custom plugins
        for plugin in set(
            itertools.chain(
                system_slot._plugin_dependencies, default_app_slot._plugin_dependencies
            )
        ):
            if not plugin.esm:
                continue

            model.vue_app_use.append(plugin.name)

            model.add_extra_import_map(
                plugin.name, resource.record_resource(plugin.esm)
            )

            if plugin.css:
                for css_link in plugin.css:
                    model.css_links.append(resource.record_resource(css_link))

        # css file link to web static link
        for link in html_resource.get_valid_css_links(
            default_html_resource._css_links_manager
        ):
            if isinstance(link, Path):
                model.css_links.append(resource.record_resource(link))
            else:
                model.css_links.append(link)

        # js file link to web static link
        for info in html_resource.get_valid_js_links(
            default_html_resource._js_links_manager
        ):
            link = (
                resource.record_resource(info.link)
                if isinstance(info.link, Path)
                else info.link
            )
            model.js_links.append(JsLink(link))

        for js_code in itertools.chain(
            html_resource._script_tags, default_html_resource._script_tags
        ):
            model.script_tags.append(js_code)

        for sylte_tag in StyleTag.merge_by_group_id(
            itertools.chain(
                html_resource._style_tags, default_html_resource._style_tags
            )
        ):
            model.style_tags.append(sylte_tag)

        model.prefix = request.headers.get(
            "X-Forwarded-Prefix", request.scope.get("root_path", "")
        )

        return web_template.render_web_html(model)

    def _update_page_info(self, request: Request, page_info: PageInfo):
        app = get_app_slot()

        app._page_path = page_info.path
        app._page_params = request.path_params
        app._query_params = dict(request.query_params)

    def _remove_route(self, path: str) -> None:
        self.app.routes[:] = [
            r for r in self.app.routes if getattr(r, "path", None) != path
        ]

    def try_close_server(self):
        UvicornServer.instance.should_exit = True

    def run(
        self,
        host="0.0.0.0",
        port=8080,
        reload: bool = True,
        reload_dirs: str = ".",
        reload_includes: str = "*.py",
        reload_excludes: str = ".*, .py[cod], .sw.*, ~*",
        log_level="info",
        workers: int | None = None,
        uds: str | None = None,
        **kwargs: Any,
    ):
        if multiprocessing.current_process().name != "MainProcess":
            return

        if reload and not hasattr(__main__, "__file__"):
            reload = False

        config = uvicorn.Config(
            APP_IMPORT_STRING if reload else self.app,
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            workers=workers,
            uds=uds,
            reload_includes=_split_args(reload_includes) if reload else None,
            reload_excludes=_split_args(reload_excludes) if reload else None,
            reload_dirs=_split_args(reload_dirs) if reload else None,
            **kwargs,
        )

        UvicornServer.create_singleton(config, [debug_mode_router.when_server_reload])

        if config.should_reload:
            ChangeReload(config, target=UvicornServer.instance.run, sockets=[]).run()
        else:
            UvicornServer.instance.run()

        if config.uds:
            os.remove(config.uds)  # pragma: py-win32

    def run_with(self, app):
        assert isinstance(app, FastAPI), "app must be a FastAPI instance"

    @staticmethod
    def add_instaui_static(app: FastAPI):
        app.mount(
            INSTAUI_STATIC_URL,
            StaticFiles(directory=consts._STATIC_DIR),
            name=INSTAUI_STATIC_URL,
        )


def _split_args(args: str):
    return [a.strip() for a in args.split(",")]


@contextmanager
def _execute_request_lifespans():
    events = [iter(event()) for event in get_launch_collector().page_request_lifespans]
    for event in events:
        next(event)

    yield

    for event in events:
        try:
            next(event)
        except StopIteration:
            pass
