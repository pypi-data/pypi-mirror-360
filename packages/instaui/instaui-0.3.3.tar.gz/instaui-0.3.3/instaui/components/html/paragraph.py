from __future__ import annotations
from typing import TYPE_CHECKING, Any, Union
from instaui.components.element import Element

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Paragraph(Element):
    """
    A component class representing an HTML `<p>` (paragraph) element.

    Args:
        text (Union[str, TMaybeRef[Any]]):The text content of the paragraph.
                                          - If a string is provided, the content is static.
                                          - If a `TMaybeRef` object is provided, the content
                                            will reactively update when the referenced value changes.
    """

    def __init__(
        self,
        text: Union[str, TMaybeRef[Any]],
    ):
        super().__init__("p")
        self.props(
            {
                "innerText": text,
            }
        )
