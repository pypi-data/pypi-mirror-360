from __future__ import annotations
from typing import Any, Dict, Mapping, Optional, Union

from instaui.common.jsonable import Jsonable

from instaui.runtime._app import get_current_scope
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from instaui.vars.mixin_types.var_type import VarMixin
from instaui.vars.mixin_types.element_binding import (
    ElementBindingMixin,
    ElementBindingProtocol,
)
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.vars.mixin_types.pathable import CanPathPropMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin


class VueComputed(
    Jsonable,
    PathVar,
    VarMixin,
    CanInputMixin,
    ObservableMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
):
    def __init__(
        self,
        fn_code: str,
        bindings: Optional[Mapping[str, Union[ElementBindingProtocol, Any]]] = None,
    ) -> None:
        self.code = fn_code
        self._bindings = bindings
        scope = get_current_scope()
        self.__register_info = scope.register_vue_computed_task(self)

        self._sid = scope.id
        self._id = scope.generate_vars_id()

        if bindings:
            const_bind = []
            self.bind = {}

            for k, v in bindings.items():
                is_binding = isinstance(v, ElementBindingMixin)
                self.bind[k] = v._to_element_binding_config() if is_binding else v
                const_bind.append(int(not is_binding))

            if any(i == 1 for i in const_bind):
                self.const = const_bind

    def __to_binding_config(self):
        return {
            "id": self.__register_info.var_id,
            "sid": self.__register_info.scope_id,
        }

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_pathable_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_observable_config(self):
        return self.__to_binding_config()

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__register_info.var_id
        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref


TVueComputed = VueComputed
