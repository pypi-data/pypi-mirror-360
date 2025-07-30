from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
from instaui.components.element import Element
from instaui.components.value_element import ValueElement
from instaui.components.mixins import CanDisabledMixin
from ._mixins import InputEventMixin

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Textarea(InputEventMixin, CanDisabledMixin, ValueElement[str]):
    def __init__(
        self,
        value: Union[str, TMaybeRef[str], None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
        disabled: Optional[TMaybeRef[bool]] = None,
    ):
        super().__init__("textarea", value, is_html_component=True)

        if disabled is not None:
            self.props({"disabled": disabled})
        if model_value is not None:
            self.props({"value": model_value})

    def _input_event_mixin_element(self) -> Element:
        return self
