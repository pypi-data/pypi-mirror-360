from __future__ import annotations
from typing import Dict
from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope
from instaui.vars._types import OutputSetType
from instaui.vars.mixin_types.py_binding import CanOutputMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin


class ElementRef(Jsonable, CanOutputMixin, ElementBindingMixin):
    def __init__(self) -> None:
        scope = get_current_scope()
        self.__register_info = scope.register_element_ref_task(self)

    def __to_binding_config(
        self,
    ):
        return {
            "id": self.__register_info.var_id,
            "sid": self.__register_info.scope_id,
        }

    def _to_output_config(self):
        return self.__to_binding_config()

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__register_info.var_id

        return data

    def _to_element_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.ElementRefAction


def run_element_method(method_name: str, *args, **kwargs):
    return {
        "method": method_name,
        "args": args,
    }
