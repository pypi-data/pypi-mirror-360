from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union
from instaui.components.element import Element

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Span(Element):
    def __init__(
        self,
        text: Union[str, TMaybeRef[Any]],
    ):
        super().__init__("span")
        self.props(
            {
                "innerText": text,
            }
        )
