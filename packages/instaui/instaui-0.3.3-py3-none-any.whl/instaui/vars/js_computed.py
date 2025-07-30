from __future__ import annotations
import typing

from instaui.common.jsonable import Jsonable

from instaui.runtime._app import get_current_scope
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from instaui.vars.mixin_types.var_type import VarMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.vars.mixin_types.pathable import CanPathPropMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.common_type import TObservableInput
from instaui._helper import observable_helper


class JsComputed(
    Jsonable,
    PathVar,
    VarMixin,
    ObservableMixin,
    CanInputMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
):
    """
    A client-side computed property that evaluates JavaScript code to derive reactive values.

    Args:
        inputs (typing.Optional[typing.Sequence[TObservableInput]], optional): Reactive data sources to monitor.
                                                  Changes to these values trigger re-computation.
        code (str): JavaScript code to execute for computing the value.
        async_init_value (typing.Optional[typing.Any], optional): Initial value to use before first successful async evaluation.

    # Example:
    .. code-block:: python
        a = ui.state(0)

        plus_one = ui.js_computed(inputs=[a], code="a=> a+1")

        html.number(a)
        ui.label(plus_one)
    """

    def __init__(
        self,
        *,
        inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
        code: str,
        async_init_value: typing.Optional[typing.Any] = None,
        deep_compare_on_input: bool = False,
    ) -> None:
        self.code = code
        self._org_inputs = inputs or []

        scope = get_current_scope()
        self.__register_info = scope.register_js_computed_task(self)

        self._inputs, self._is_slient_inputs, self._is_data = (
            observable_helper.analyze_observable_inputs(list(inputs or []))
        )

        self._async_init_value = async_init_value
        self._deep_compare_on_input = deep_compare_on_input

    def __to_binding_config(self):
        return {
            "id": self.__register_info.var_id,
            "sid": self.__register_info.scope_id,
        }

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> typing.Dict:
        return self.__to_binding_config()

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_pathable_binding_config(self) -> typing.Dict:
        return self.__to_binding_config()

    def _to_observable_config(self):
        return self.__to_binding_config()

    def _to_json_dict(self):
        data = super()._to_json_dict()

        data["id"] = self.__register_info.var_id

        if self._inputs:
            data["inputs"] = self._inputs

        if sum(self._is_slient_inputs) > 0:
            data["slient"] = self._is_slient_inputs

        if sum(self._is_data) > 0:
            data["data"] = self._is_data

        if self._async_init_value is not None:
            data["asyncInit"] = self._async_init_value

        if self._deep_compare_on_input is not False:
            data["deepEqOnInput"] = 1

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref


TJsComputed = JsComputed
