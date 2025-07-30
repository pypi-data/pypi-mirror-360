from __future__ import annotations
from typing import (
    Optional,
)
from instaui.components.element import Element

from instaui.vars.types import TMaybeRef


class Link(Element):
    def __init__(
        self,
        href: Optional[TMaybeRef[str]] = None,
        *,
        text: Optional[TMaybeRef[str]] = None,
    ):
        super().__init__("a")

        if text is not None:
            self.props(
                {
                    "innerText": text,
                }
            )

        if href is not None:
            self.props(
                {
                    "href": href,
                }
            )
