from typing import Any, TypeVar, Union
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin

_T = TypeVar("_T")


def is_bindable(obj: Any):
    return isinstance(
        obj, (CanInputMixin, CanOutputMixin, ObservableMixin, ElementBindingMixin)
    )


TBindable = Union[
    CanInputMixin, CanOutputMixin, ObservableMixin, ElementBindingMixin[_T]
]
