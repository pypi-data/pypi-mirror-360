from __future__ import annotations
import threading
from typing import (
    Callable,
    Dict,
    Generic,
    TypeVar,
)
from dataclasses import dataclass

from instaui.runtime.context import get_context
from instaui.runtime._app import update_web_server_info
from instaui.systems import func_system
from . import _utils


ASYNC_URL = "/instaui/watch/async"
SYNC_URL = "/instaui/watch/sync"

update_web_server_info(watch_url=SYNC_URL, watch_async_url=ASYNC_URL)

_watch_handlers: Dict[str, _utils.HandlerInfo] = {}
dict_lock = threading.Lock()


def register_handler(key: str, handler: Callable, outputs_binding_count: int):
    if key in _watch_handlers:
        return
    with dict_lock:
        _watch_handlers[key] = _utils.HandlerInfo.from_handler(
            handler, outputs_binding_count
        )


def get_handler_info(key: str) -> _utils.HandlerInfo:
    return _watch_handlers.get(key)  # type: ignore


def get_statistics_info():
    return {
        "_watch_handlers count": len(_watch_handlers),
        "_watch_handlers keys": list(_watch_handlers.keys()),
    }


def create_handler_key(page_path: str, handler: Callable):
    _, lineno, _ = func_system.get_function_location_info(handler)

    if get_context().debug_mode:
        return f"path:{page_path}|line:{lineno}"
    return f"{page_path}|{lineno}"


_TWatchStateValue = TypeVar("_TWatchStateValue")


@dataclass(frozen=True)
class WatchState(Generic[_TWatchStateValue]):
    new_value: _TWatchStateValue
    old_value: _TWatchStateValue
    modified: bool
