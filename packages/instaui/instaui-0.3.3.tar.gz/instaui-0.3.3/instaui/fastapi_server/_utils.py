from typing import Any, Dict, List, Optional, Sequence
from instaui.runtime._app import get_app_slot
from instaui.response import response_data
import pydantic


class ResponseData(pydantic.BaseModel):
    values: Optional[List[Any]] = None
    types: Optional[Sequence[int]] = None


def update_app_page_info(data: Dict):
    app = get_app_slot()

    page_info = data.get("page", {})
    app._page_path = page_info["path"]

    if "params" in page_info:
        app._page_params = page_info["params"]

    if "queryParams" in page_info:
        app._query_params = page_info["queryParams"]


def response_web_data(outputs_binding_count: int, result: Any):
    return ResponseData(**response_data(outputs_binding_count, result))
