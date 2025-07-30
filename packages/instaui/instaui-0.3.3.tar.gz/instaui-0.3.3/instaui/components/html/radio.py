from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from instaui.components.element import Element
from instaui.components.value_element import ValueElement
from ._mixins import InputEventMixin

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


_T_value = str


class Radio(InputEventMixin, ValueElement[_T_value]):
    def __init__(
        self,
        value: Optional[TMaybeRef[_T_value]] = None,
        *,
        model_value: Optional[_T_value] = None,
        id: Optional[TMaybeRef[str]] = None,
        name: Optional[TMaybeRef[str]] = None,
    ):
        super().__init__("input", value, is_html_component=True)
        self.props({"type": "radio"})

        self.props(
            {
                "id": id,
                "name": name,
            }
        )

        if model_value is not None:
            self.props({"value": model_value})

    def _input_event_mixin_element(self) -> Element:
        return self
