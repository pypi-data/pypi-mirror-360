from __future__ import annotations
from typing import Any, Union
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui import ui_system_var_type as ui_vars_type


class Heading(Element):
    def __init__(
        self,
        text: Union[str, TMaybeRef[Any]],
        *,
        size: Union[TMaybeRef[str], ui_vars_type.TSize, None] = None,
        weight: Union[TMaybeRef[str], ui_vars_type.TWeight, None] = None,
        align: Union[TMaybeRef[str], ui_vars_type.TAlign, None] = None,
    ):
        """
        Creates a heading element with customizable text content and styling properties.


        Args:
            text (Union[str, TMaybeRef[Any]]): The text content of the heading. Can be a static
                string or a reactive reference (e.g., state object).
            size (Union[TMaybeRef[str], TSize, None], optional): Controls the heading size.
                Accepts values from "1" to "9". Defaults to None.
            weight (Union[TMaybeRef[str], TWeight, None], optional): Sets font weight.
                Acceptable values: "light", "regular", "medium", "bold". Defaults to None.
            align (Union[TMaybeRef[str], TAlign, None], optional): Controls text alignment.
                Valid options: "left", "center", "right". Defaults to None.

        Example:
        .. code-block:: python
            size = ui.state("6")
            text = ui.state("test")
            align = ui.state("left")

            html.select.from_list(["1", "2", "3", "4", "5", "6", "7", "8", "9"], size)
            html.select.from_list(["left", "center", "right"], align)

            with ui.container():
                html.input(text)
                ui.heading(text, size=size, align=align)
        """
        super().__init__("heading")

        self.props({"text": text, "size": size, "weight": weight, "align": align})
