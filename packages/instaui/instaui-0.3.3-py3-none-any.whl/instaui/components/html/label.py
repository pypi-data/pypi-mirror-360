from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Union
from instaui.components.element import Element

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Label(Element):
    def __init__(
        self,
        text: Union[Any, TMaybeRef[Any], None] = None,
        *,
        for_: Optional[TMaybeRef[str]] = None,
    ):
        super().__init__("label")

        self.props(
            {
                "innerText": text,
                "for": for_,
            }
        )
