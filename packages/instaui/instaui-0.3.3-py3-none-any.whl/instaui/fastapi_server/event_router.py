import inspect
from typing import Dict
from fastapi import FastAPI

from instaui.handlers import event_handler
from instaui.runtime.context import get_context

from . import _utils


def create_router(app: FastAPI):
    _async_handler(app)
    _sync_handler(app)


def _async_handler(app: FastAPI):
    @app.post(event_handler.ASYNC_URL)
    async def _(data: Dict):
        handler = _get_handler(data)
        if handler is None:
            return {"error": "event handler not found"}

        assert inspect.iscoroutinefunction(handler.fn), (
            "handler must be a coroutine function"
        )

        _utils.update_app_page_info(data)

        result = await handler.fn(*handler.get_handler_args(_get_binds_from_data(data)))
        return _utils.response_web_data(handler.outputs_binding_count, result)


def _sync_handler(app: FastAPI):
    @app.post(event_handler.SYNC_URL)
    def _(data: Dict):
        handler = _get_handler(data)
        if handler is None:
            return {"error": "event handler not found"}

        _utils.update_app_page_info(data)

        result = handler.fn(*handler.get_handler_args(_get_binds_from_data(data)))

        return _utils.response_web_data(handler.outputs_binding_count, result)

    if get_context().debug_mode:

        @app.get("/instaui/event-infos", tags=["instaui-debug"])
        def event_infos():
            return event_handler.get_statistics_info()


def _get_handler(data: Dict):
    return event_handler.get_handler(data["hKey"])


def _get_binds_from_data(data: Dict):
    return [bind for bind in data.get("bind", [])]
