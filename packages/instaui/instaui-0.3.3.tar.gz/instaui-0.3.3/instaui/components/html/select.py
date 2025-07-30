from __future__ import annotations
from typing import (
    Dict,
    List,
    Optional,
    Union,
)
from instaui.components.value_element import ValueElement
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from instaui.vars.types import TMaybeRef
from instaui.components.vfor import VFor
from instaui.components.mixins import CanDisabledMixin

_T_Select_Value = Union[List[str], str]


class Select(CanDisabledMixin, ValueElement[Union[List[str], str]]):
    def __init__(
        self,
        value: Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
    ):
        super().__init__("select", value, is_html_component=True)

        if model_value is not None:
            self.props({"value": model_value})

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        self.on("change", handler)
        return self

    @classmethod
    def from_list(
        cls,
        options: TMaybeRef[List],
        value: Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
    ) -> Select:
        with cls(value, model_value=model_value) as select:
            with VFor(options) as item:
                Select.Option(item)  # type: ignore

        return select

    @classmethod
    def from_records(
        cls,
        options: TMaybeRef[List[Dict]],
        value: Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
    ) -> Select:
        with cls(value, model_value=model_value) as select:
            with VFor(options) as item:
                Select.Option(item["text"], item["value"])  # type: ignore

        return select

    class Option(Element, CanDisabledMixin):
        def __init__(
            self,
            text: Optional[TMaybeRef[str]] = None,
            value: Optional[TMaybeRef[str]] = None,
            disabled: Optional[TMaybeRef[bool]] = None,
        ):
            props = {
                key: value
                for key, value in {
                    "text": text,
                    "value": value,
                    "disabled": disabled,
                }.items()
                if value is not None
            }
            super().__init__("option")

            self._props.update(props)
