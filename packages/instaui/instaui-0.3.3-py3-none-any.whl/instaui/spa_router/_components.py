from __future__ import annotations
import typing
from instaui import html
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef


class RouterLink(Element):
    def __init__(self, text: TMaybeRef[str], *, to: str):
        super().__init__("router-link")

        self.props({"to": to})

        if text is not None:
            with self.add_slot("default"):
                html.span(text)

    @classmethod
    def by_name(
        cls,
        text: TMaybeRef[str],
        *,
        name: str,
        params: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ) -> RouterLink:
        to: typing.Dict = {"name": name}
        if params:
            to["params"] = params

        return cls(text, to=to)  # type: ignore


class RouterView(Element):
    def __init__(self):
        super().__init__("router-view")
