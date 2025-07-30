from __future__ import annotations
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef


class Container(Element):
    """
    Creates a layout container element with configurable width and spacing properties.

    A flexible container component for structuring content layouts, providing controls for
    maximum width and internal padding. The container is horizontally centered by default
    through auto margins.

    Args:
        max_width (TMaybeRef[str], optional): Sets the maximum width of the container.
            Accepts CSS width values (e.g., "800px", "100%", "75vw"). Defaults to "800px".
        padding (TMaybeRef[str], optional): Controls internal spacing between container
            edges and content. Accepts CSS padding values (e.g., "0.25rem", "1em", "10px").
            Defaults to "0.25rem".
    """

    def __init__(
        self,
        max_width: TMaybeRef[str] = "800px",
        *,
        padding: TMaybeRef[str] = "0.25rem",
    ):
        super().__init__("div")

        self.style({"max-width": max_width, "padding": padding}).style(
            "margin-left:auto;margin-right:auto"
        )
