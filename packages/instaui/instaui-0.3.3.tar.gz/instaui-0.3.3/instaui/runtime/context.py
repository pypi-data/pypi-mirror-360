from __future__ import annotations
from typing import Any, Dict, Optional
from instaui import consts
from ._app import get_app_slot


class Context:
    _instance: Optional[Context] = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self):
        self._app_mode: consts._T_App_Mode = "web"
        self._debug_mode: bool = False
        self._page_params: Dict[str, Any] = {}

    @property
    def app_mode(self):
        return self._app_mode

    @property
    def debug_mode(self):
        return self._debug_mode

    @property
    def page_path(self):
        return get_app_slot().page_path

    @property
    def page_params(self):
        return get_app_slot().page_params

    @property
    def query_params(self):
        return get_app_slot().query_params


def get_context():
    return Context.get_instance()


def set_debug(debug=True):
    get_context()._debug_mode = debug
