from __future__ import annotations
from typing import Callable, Dict, List, Optional
from instaui.consts import _T_App_Mode
from instaui.page_info import PageInfo
from instaui.systems import func_system


class LaunchCollector:
    _instance: Optional[LaunchCollector] = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self._page_router: Dict[str, PageInfo] = {}
        self._page_request_lifespans: Dict[int, Callable] = {}
        self._app_mode: _T_App_Mode = "web"

    @property
    def page_request_lifespans(self) -> List[Callable]:
        return list(self._page_request_lifespans.values())

    def register_page(self, info: PageInfo) -> None:
        self._page_router[info.path] = info

    def add_page_request_lifespan(self, lifespan: Callable) -> int:
        """Register a function to be called on each page request.

        Args:
            lifespan (Callable):  A function to be called on each page request.

        Returns:
            int:  A unique key to identify the registered lifespan function.
        """
        key = id(lifespan)
        self._page_request_lifespans[key] = func_system.make_fn_to_generator(lifespan)

        return key

    def remove_page_request_lifespan(self, key: int) -> None:
        if key in self._page_request_lifespans:
            del self._page_request_lifespans[key]

    def set_app_mode(self, mode: _T_App_Mode) -> None:
        self._app_mode = mode


def get_launch_collector() -> LaunchCollector:
    return LaunchCollector.get_instance()
