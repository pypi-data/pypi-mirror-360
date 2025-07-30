from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
)
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from instaui.vars.types import TMaybeRef
from instaui.components.mixins import CanDisabledMixin

if TYPE_CHECKING:
    pass


class Button(Element, CanDisabledMixin):
    def __init__(
        self,
        text: Optional[TMaybeRef[str]] = None,
    ):
        super().__init__("button")

        if text is not None:
            self.props(
                {
                    "innerText": text,
                }
            )

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        self.on("click", handler, extends=extends)
        return self
