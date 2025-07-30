from __future__ import annotations
import threading
from typing import Callable, Dict, Optional, Sequence, TYPE_CHECKING
import ast
from . import _utils
from instaui.vars.event_context import DatasetEventContext
from instaui.runtime._app import update_web_server_info

if TYPE_CHECKING:
    from instaui.vars.mixin_types.py_binding import CanOutputMixin, CanInputMixin

ASYNC_URL = "/instaui/event/async"
SYNC_URL = "/instaui/event/sync"
update_web_server_info(event_url=SYNC_URL, event_async_url=ASYNC_URL)
_event_handlers: Dict[str, _utils.HandlerInfo] = {}
dict_lock = threading.Lock()


class EventDataSetTypeAdapter:
    def to_python_value(self, value, *args, **kwargs):
        return ast.literal_eval(value)


def register_event_handler(
    key: str,
    handler: Callable,
    outputs_binding: Optional[Sequence[CanOutputMixin]],
    inputs_binding: Optional[Sequence[CanInputMixin]],
):
    if key in _event_handlers:
        return

    custom_type_adapter_map = {
        i: EventDataSetTypeAdapter()
        for i, binding in enumerate(inputs_binding or [])
        if isinstance(binding, DatasetEventContext)
    }

    handler_info = _utils.HandlerInfo.from_handler(
        handler,
        len(list(outputs_binding)) if outputs_binding else 0,
        custom_type_adapter_map=custom_type_adapter_map,
    )

    with dict_lock:
        _event_handlers[key] = handler_info


def get_handler(key: str) -> Optional[_utils.HandlerInfo]:
    return _event_handlers.get(key)


def get_statistics_info():
    return {
        "_event_handlers count": len(_event_handlers),
        "_event_handlers keys": list(_event_handlers.keys()),
    }


create_handler_key = _utils.create_handler_key
