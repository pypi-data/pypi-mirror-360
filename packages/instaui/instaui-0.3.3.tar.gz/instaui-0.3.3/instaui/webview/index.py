from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union
from typing_extensions import TypedDict, Unpack
import webview
import webview.http as http
from webview.guilib import GUIType

from instaui.runtime._app import get_app_slot, new_app_slot, reset_app_slot
from instaui.launch_collector import get_launch_collector

from . import resource
from . import api
from . import _utils


class WebviewWrapper:
    """Example usage:
    .. code-block:: python
        from instaui import ui

        @ui.page("/")
        def index_page():
            ui.content("Hello, world!")

        ui.webview().run()
    """

    def __init__(
        self,
        *,
        assets_path: Union[str, Path] = "./webview_assets",
        debug: bool = False,
        auto_create_window: Union[bool, str] = "/",
        on_app_mounted: Optional[Callable] = None,
    ) -> None:
        """Create a new webview wrapper.

        Args:
            assets_path (Union[str, Path], optional): Path to store assets. Defaults to "./webview_assets".
            debug (bool, optional): Whether to run in debug mode. Defaults to False.
            auto_create_window (Union[bool, str], optional): Whether to create a window automatically. If a string is provided, it will be used as the initial page URL. Defaults to "/".
            testing (bool, optional): Whether to run in testing mode. Defaults to False.
        """

        self.assets_path = (
            Path(self._get_assets_path(assets_path))
            if isinstance(assets_path, str)
            else assets_path
        )
        _utils.reset_dir(self.assets_path)
        self.debug = debug
        self.on_app_mounted = on_app_mounted

        self._auto_create_window = auto_create_window

    def create_window(
        self,
        page_url: str = "/",
    ):
        """Create a new window. Returns the window object of pywebview.

        Args:
            page_url (str, optional): Page URL to load. Defaults to "/".

        """
        launch_collector = get_launch_collector()
        with _scope():
            app = get_app_slot()
            app._page_path = page_url
            page_info = launch_collector._page_router[page_url]
            page_info.func()

            resource_info = resource.resource_to_assets(
                page_url=page_url,
                assets_path=self.assets_path,
                on_app_mounted=self.on_app_mounted,
            )

        window = webview.create_window(
            resource_info.title, resource_info.index_html_url, js_api=api.Api()
        )

        if self.on_app_mounted:

            def on_app_mounted():
                self.on_app_mounted(window)  # type: ignore

            window.expose(on_app_mounted)

        return window

    def run(self, **webview_start_args: Unpack[WebviewStartArgs]):
        """Run the webview.

        Args:
            :param func: Function to invoke upon starting the GUI loop.
            :param args: Function arguments. Can be either a single value or a tuple of
                values.
            :param localization: A dictionary with localized strings. Default strings
                and their keys are defined in localization.py.
            :param gui: Force a specific GUI. Allowed values are ``cef``, ``qt``,
                ``gtk``, ``mshtml`` or ``edgechromium`` depending on a platform.
            :param http_server: Enable built-in HTTP server. If enabled, local files
                will be served using a local HTTP server on a random port. For each
                window, a separate HTTP server is spawned. This option is ignored for
                non-local URLs.
            :param user_agent: Change user agent string.
            :param private_mode: Enable private mode. In private mode, cookies and local storage are not preserved.
                Default is True.
            :param storage_path: Custom location for cookies and other website data
            :param menu: List of menus to be included in the app menu
            :param server: Server class. Defaults to BottleServer
            :param server_args: Dictionary of arguments to pass through to the server instantiation
            :param ssl: Enable SSL for local HTTP server. Default is False.
            :param icon: Path to the icon file. Supported only on GTK/QT.
        """

        if self._auto_create_window:
            self.create_window(
                "/" if self._auto_create_window is True else self._auto_create_window
            )

        webview.start(**webview_start_args, debug=self.debug)

    @staticmethod
    def _get_assets_path(file: Union[str, Path]) -> Path:
        if isinstance(file, str):
            import inspect

            frame = inspect.currentframe().f_back.f_back.f_back.f_back.f_back  # type: ignore
            assert frame is not None
            script_file = inspect.getfile(frame)
            file = Path(script_file).parent.joinpath(file)

        return file


@contextmanager
def _scope():
    token = new_app_slot("webview")
    yield
    reset_app_slot(token)


class WebviewStartArgs(TypedDict, total=False):
    func: Union[Callable[..., None], None]
    args: Union[Iterable[Any], None]
    localization: Dict[str, str]
    gui: Union[GUIType, None]
    http_server: bool
    http_port: Union[int, None]
    user_agent: Union[str, None]
    private_mode: bool
    storage_path: Union[str, None]
    menu: List[Any]
    server: type[http.ServerType]  # type: ignore
    server_args: Dict[Any, Any]
    ssl: bool
    icon: Union[str, None]
