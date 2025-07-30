from __future__ import annotations
from typing import Literal
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.vars.js_computed import JsComputed


class Column(Element):
    def __init__(self, *, inline: TMaybeRef[bool] = False):
        super().__init__("div")

        flex = JsComputed(
            inputs=[inline], code="inline => inline? 'inline-flex' : 'flex'"
        )

        self.style("flex-direction: column;gap:var(--insta-column-gap)").style(
            {"display": flex}
        )

    def gap(self, value: TMaybeRef[str]) -> Column:
        return self.style({"gap": value})

    def align_items(
        self, value: TMaybeRef[Literal["start", "end", "center", "stretch", "revert"]]
    ) -> Column:
        return self.style({"align-items": value})
