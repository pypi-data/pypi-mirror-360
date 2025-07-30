from __future__ import annotations
from typing import (
    Any,
    Optional,
    Union,
)

from instaui.components.element import Element
from instaui.components.value_element import ValueElement


from instaui.vars.types import TMaybeRef
from ._mixins import InputEventMixin


class Checkbox(InputEventMixin, ValueElement[Union[bool, str]]):
    def __init__(
        self,
        value: Union[Union[bool, str], TMaybeRef[Union[bool, str]], None] = None,
        *,
        model_value: Optional[TMaybeRef[Union[bool, str]]] = None,
        checked: Optional[TMaybeRef[bool]] = None,
        id: Optional[Any] = None,
    ):
        super().__init__("input", value, is_html_component=True)
        self.props({"type": "checkbox"})
        if id is not None:
            self.props({"id": id})
        if checked is not None:
            self.props({"checked": checked})
        if model_value is not None:
            self.props({"value": model_value})

    def _input_event_mixin_element(self) -> Element:
        return self
