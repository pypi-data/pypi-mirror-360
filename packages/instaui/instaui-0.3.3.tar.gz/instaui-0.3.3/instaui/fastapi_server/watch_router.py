from typing import Dict
from fastapi import FastAPI
from instaui.handlers import watch_handler
from instaui.runtime.context import get_context

from . import _utils


def create_router(app: FastAPI):
    _async_handler(app)
    _sync_handler(app)


def _async_handler(app: FastAPI):
    @app.post(watch_handler.ASYNC_URL)
    async def _(data: Dict):
        hkey = data.pop("key")
        handler_info = watch_handler.get_handler_info(hkey)
        if handler_info is None:
            return {"error": "watch handler not found"}

        _utils.update_app_page_info(data)

        result = await handler_info.fn(
            *handler_info.get_handler_args(_get_binds_from_data(data))
        )
        return _utils.response_web_data(handler_info.outputs_binding_count, result)


def _sync_handler(app: FastAPI):
    @app.post(watch_handler.SYNC_URL)
    def _(data: Dict):
        hkey = data.pop("key")
        handler_info = watch_handler.get_handler_info(hkey)
        if handler_info is None:
            return {"error": "watch handler not found"}

        _utils.update_app_page_info(data)

        result = handler_info.fn(
            *handler_info.get_handler_args(_get_binds_from_data(data))
        )
        return _utils.response_web_data(handler_info.outputs_binding_count, result)

    if get_context().debug_mode:

        @app.get("/instaui/watch-infos", tags=["instaui-debug"])
        def watch_infos():
            return watch_handler.get_statistics_info()


def _get_binds_from_data(data: Dict):
    return data.get("input", [])
