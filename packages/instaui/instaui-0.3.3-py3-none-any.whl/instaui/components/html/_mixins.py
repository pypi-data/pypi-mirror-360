from __future__ import annotations
import abc
from typing import TYPE_CHECKING, List, Optional
from instaui.event.event_mixin import EventMixin


if TYPE_CHECKING:
    from instaui.components.element import Element


class InputEventMixin:
    @abc.abstractmethod
    def _input_event_mixin_element(self) -> Element:
        pass

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
        key: Optional[str] = None,
    ):
        self._input_event_mixin_element().on("change", handler, extends=extends)
        return self

    def on_input(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
        key: Optional[str] = None,
    ):
        self._input_event_mixin_element().on("input", handler, extends=extends)
        return self
