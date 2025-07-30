from __future__ import annotations
from typing import (
    Any,
    Dict,
)

from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.path_var import PathVar

from .mixin_types.var_type import VarMixin
from .mixin_types.py_binding import CanInputMixin, CanOutputMixin
from .mixin_types.element_binding import ElementBindingMixin
from .mixin_types.pathable import CanPathPropMixin
from .mixin_types.str_format_binding import StrFormatBindingMixin


class ConstData(
    Jsonable,
    PathVar,
    VarMixin,
    CanInputMixin,
    CanOutputMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
):
    def __init__(self, value: Any = None) -> None:
        self.value = value  # type: ignore

        scope = get_current_scope()
        self.__register_info = scope.register_data_task(self)

    def __to_binding_config(self):
        return {
            "id": self.__register_info.var_id,
            "sid": self.__register_info.scope_id,
        }

    def _to_pathable_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_output_config(self):
        return self.__to_binding_config()

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__register_info.var_id

        return data

    def _to_event_output_type(self) -> OutputSetType:
        raise TypeError("ConstData cannot be used as an output")

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Data


TConstData = ConstData
