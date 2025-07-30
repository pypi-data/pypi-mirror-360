from typing import Dict, Tuple, TypeVar, cast
from instaui.vars.ref import Ref
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.pathable import CanPathPropMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.common.jsonable import Jsonable

from pydantic import BaseModel, RootModel

_T = TypeVar("_T")


_ProxyModel = RootModel


class RefProxy(
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
    Jsonable,
):
    def __init__(self, instance: BaseModel, *, deep_compare: bool = False) -> None:
        data = instance.model_dump()
        self._ref_ = Ref(data, deep_compare=deep_compare)
        self._prop_names_ = set(data.keys()) if isinstance(data, dict) else set()

    @property
    def __ref_(self):
        return super().__getattribute__("_ref_")

    def __getattribute__(self, name):
        if name not in super().__getattribute__("_prop_names_"):
            return super().__getattribute__(name)

        return self.__ref_[name]

    def __getitem__(self, name):
        return self.__ref_[name]

    def inverse(self):
        return self.__ref_.inverse()

    def __add__(self, other: str):
        return self.__ref_ + other

    def __radd__(self, other: str):
        return other + self.__ref_

    def _to_element_binding_config(self) -> Dict:
        return self.__ref_._to_element_binding_config()

    def _to_input_config(self):
        return self.__ref_._to_input_config()

    def _to_observable_config(self):
        return self.__ref_._to_observable_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__ref_._to_path_prop_binding_config()

    def _to_output_config(self):
        return self.__ref_._to_output_config()

    def _to_str_format_binding(self, order: int) -> Tuple[str, str]:
        return self.__ref_._to_str_format_binding(order)

    def _to_json_dict(self):
        return self.__ref_._to_json_dict()

    def _to_event_output_type(self) -> OutputSetType:
        return self.__ref_._to_event_output_type()

    def _to_event_input_type(self) -> InputBindingType:
        return self.__ref_._to_event_input_type()


class StateModel(BaseModel, Jsonable):
    pass

    def _to_json_dict(self):
        return self.model_dump()


def state(value: _T, *, deep_compare: bool = False) -> _T:
    """
    Creates a reactive state object that tracks changes and notifies dependencies.

    Args:
        value (_T): The initial value to wrap in a reactive state container.
                   Can be any type (primitive, object, or complex data structure).

    # Example:
    .. code-block:: python
        from instaui import ui,html
        count = ui.state(0)

        html.number(count)
        ui.label(count)
    """
    if isinstance(value, RefProxy):
        return value
    obj = RefProxy(_ProxyModel(value), deep_compare=deep_compare)
    return cast(_T, obj)
