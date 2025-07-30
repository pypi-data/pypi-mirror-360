from __future__ import annotations
from typing import Optional
from fastapi import Request
from contextvars import ContextVar, Token

current_request_ctx: ContextVar[Optional[Request]] = ContextVar(
    "current_request", default=None
)


def set_current_request(request: Request):
    return current_request_ctx.set(request)


def reset_current_request(token: Token) -> None:
    current_request_ctx.reset(token)


def get_current_request() -> Request:
    return current_request_ctx.get()  # type: ignore
