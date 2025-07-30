from __future__ import annotations
from typing import (
    Dict,
)
from instaui.common.jsonable import Jsonable
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from .mixin_types.py_binding import CanInputMixin
from .mixin_types.element_binding import ElementBindingMixin
from .mixin_types.pathable import CanPathPropMixin


class BindingSlotPropItem(
    Jsonable,
    PathVar,
    ElementBindingMixin,
    CanInputMixin,
    CanPathPropMixin,
):
    def __init__(self, name: str, sid: str, var_id: str) -> None:
        super().__init__()
        self._name = name
        self._sid = sid
        self._id = var_id

    def __to_binding_config(self):
        data: Dict = {
            "sid": self._sid,
            "id": self._id,
        }

        return data

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_pathable_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_json_dict(self):
        data: Dict = {
            "id": self._id,
        }

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref
