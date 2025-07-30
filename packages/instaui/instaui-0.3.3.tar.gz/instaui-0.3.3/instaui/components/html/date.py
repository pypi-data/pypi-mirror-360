from __future__ import annotations
from typing import TYPE_CHECKING, Union

from instaui.components.value_element import ValueElement
from ._mixins import InputEventMixin

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef
    from instaui.components.element import Element

_T_value = str


class Date(InputEventMixin, ValueElement[_T_value]):
    def __init__(
        self,
        value: Union[_T_value, TMaybeRef[_T_value], None] = None,
        *,
        model_value: Union[_T_value, TMaybeRef[_T_value], None] = None,
    ):
        super().__init__("input", value, is_html_component=True)
        self.props({"type": "date"})

        if model_value is not None:
            self.props({"value": model_value})

    def _input_event_mixin_element(self) -> Element:
        return self
