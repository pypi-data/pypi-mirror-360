from __future__ import annotations
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.vars.js_computed import JsComputed


class Row(Element):
    def __init__(self, *, inline: TMaybeRef[bool] = False):
        super().__init__("div")
        flex = JsComputed(
            inputs=[inline], code="inline => inline? 'inline-flex' : 'flex'"
        )

        self.style("gap:var(--insta-row-gap)").style({"display": flex})

    def gap(self, value: str) -> Row:
        return self.style({"gap": value})
