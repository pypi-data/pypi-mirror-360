from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, Union
from instaui.components.element import Element

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Heading(Element):
    def __init__(
        self,
        text: Union[str, TMaybeRef[Any]],
        *,
        level: Literal[1, 2, 3, 4, 5, 6] = 1,
    ):
        super().__init__(f"h{level}")
        self.props(
            {
                "innerText": text,
            }
        )


class H1(Heading):
    def __init__(self, text: Union[str, TMaybeRef[Any]]):
        super().__init__(text, level=1)


class H2(Heading):
    def __init__(self, text: Union[str, TMaybeRef[Any]]):
        super().__init__(text, level=2)


class H3(Heading):
    def __init__(self, text: Union[str, TMaybeRef[Any]]):
        super().__init__(text, level=3)


class H4(Heading):
    def __init__(self, text: Union[str, TMaybeRef[Any]]):
        super().__init__(text, level=4)


class H5(Heading):
    def __init__(self, text: Union[str, TMaybeRef[Any]]):
        super().__init__(text, level=5)


class H6(Heading):
    def __init__(self, text: Union[str, TMaybeRef[Any]]):
        super().__init__(text, level=6)
