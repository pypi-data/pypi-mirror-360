from __future__ import annotations
from typing import (
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
    overload,
)

from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.path_var import PathVar

from .mixin_types.var_type import VarMixin
from .mixin_types.py_binding import CanInputMixin, CanOutputMixin
from .mixin_types.observable import ObservableMixin
from .mixin_types.element_binding import ElementBindingMixin
from .mixin_types.pathable import CanPathPropMixin
from .mixin_types.str_format_binding import StrFormatBindingMixin


_T_Value = TypeVar("_T_Value")


class Ref(
    Jsonable,
    PathVar,
    VarMixin,
    ObservableMixin,
    CanInputMixin,
    CanOutputMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin[_T_Value],
    Generic[_T_Value],
):
    VAR_TYPE = "var"

    def __init__(
        self, value: Optional[_T_Value] = None, *, deep_compare: bool = False
    ) -> None:
        self.value = value  # type: ignore
        scope = get_current_scope()
        self.__register_info = scope.register_ref_task(self)

        self._deep_compare = deep_compare
        self._debounced = None

    def debounced(self, secounds: float):
        self._debounced = secounds
        return self

    def __to_binding_config(self):
        return {
            "id": self.__register_info.var_id,
            "sid": self.__register_info.scope_id,
        }

    def _to_pathable_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_observable_config(self):
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

        if self._debounced is not None:
            data["debounced"] = self._debounced

        if self._deep_compare is True:
            data["deepCompare"] = True

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref


@overload
def ref(value: Ref[_T_Value], *, deep_compare: bool = False) -> Ref[_T_Value]: ...


@overload
def ref(
    value: Optional[_T_Value] = None, *, deep_compare: bool = False
) -> Ref[_T_Value]: ...


def ref(
    value: Union[Ref[_T_Value], _T_Value, None] = None, *, deep_compare: bool = False
):
    if isinstance(value, Ref):
        return value
    return Ref(value, deep_compare=deep_compare)
