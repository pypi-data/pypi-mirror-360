from typing import Any, Union
from .ref import Ref
from .js_computed import JsComputed
from .vue_computed import VueComputed
from .web_computed import WebComputed


from ._types import _T_Value
from .mixin_types.element_binding import ElementBindingMixin


TRefOrComputed = Union[
    Ref[_T_Value],
    VueComputed,
    JsComputed,
    WebComputed[Any, _T_Value],
]
TMaybeRef = Union[
    ElementBindingMixin[_T_Value],
    WebComputed,
    VueComputed,
    JsComputed,
    _T_Value,
]
