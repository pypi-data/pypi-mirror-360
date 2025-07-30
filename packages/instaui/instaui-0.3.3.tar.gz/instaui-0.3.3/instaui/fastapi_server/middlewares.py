from __future__ import annotations
from typing import Any, Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from instaui.runtime import new_app_slot, reset_app_slot
from .request_context import set_current_request


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        set_current_request(request)
        system_slot_token = new_app_slot("web")

        try:
            response = await call_next(request)
        finally:
            reset_app_slot(system_slot_token)

        return response


class NoCacheDebugModeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        response = await call_next(request)

        if request.url.path.endswith((".js", ".css")):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response
