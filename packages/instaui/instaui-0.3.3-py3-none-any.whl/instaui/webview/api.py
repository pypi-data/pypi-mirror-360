from typing import Dict


from instaui.runtime._app import get_app_slot
from instaui.handlers import watch_handler
from instaui.handlers import event_handler
from instaui.response import response_data


class Api:
    def watch_call(self, data: Dict):
        hkey = data.pop("key")
        handler_info = watch_handler.get_handler_info(hkey)
        if handler_info is None:
            return {"error": "watch handler not found"}

        update_app_page_info(data)

        result = handler_info.fn(
            *handler_info.get_handler_args(_get_binds_from_data(data))
        )
        return response_data(handler_info.outputs_binding_count, result)

    def event_call(self, data: Dict):
        handler = event_handler.get_handler(data["hKey"])
        if handler is None:
            raise ValueError("event handler not found")

        update_app_page_info(data)

        args = [bind for bind in data.get("bind", [])]

        result = handler.fn(*handler.get_handler_args(args))
        return response_data(handler.outputs_binding_count, result)


def update_app_page_info(data: Dict):
    app = get_app_slot()

    page_info = data.get("page", {})
    app._page_path = page_info["path"]

    if "params" in page_info:
        app._page_params = page_info["params"]

    if "queryParams" in page_info:
        app._query_params = page_info["queryParams"]


def _get_binds_from_data(data: Dict):
    return data.get("input", [])
