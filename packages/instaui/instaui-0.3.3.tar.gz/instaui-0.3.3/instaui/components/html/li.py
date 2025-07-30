from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union
from instaui.components.element import Element

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Li(Element):
    def __init__(
        self,
        text: Union[Any, TMaybeRef[Any], None] = None,
    ):
        super().__init__("li")

        if text:
            self.props({"innerText": text})
