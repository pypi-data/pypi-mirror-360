from __future__ import annotations
from typing import (
    Literal,
    Optional,
    TypeVar,
    Union,
)
from instaui.vars.types import TMaybeRef
from instaui.vars.js_computed import JsComputed
from instaui.components.element import Element
from instaui.vars.mixin_types.observable import ObservableMixin

_T = TypeVar("_T")


class Grid(Element):
    def __init__(
        self,
        *,
        rows: Optional[TMaybeRef[Union[int, str]]] = None,
        columns: Optional[TMaybeRef[Union[int, str]]] = None,
        template: Optional[TMaybeRef[str]] = None,
    ):
        '''Grid component

        Args:
            rows (Optional[TMaybeRef[Union[int, str]]], optional): Number of rows or template for rows. Defaults to None.
            columns (Optional[TMaybeRef[Union[int, str]]], optional): Number of columns or template for columns. Defaults to None.
            template (Optional[TMaybeRef[str]], optional): Template for grid. Defaults to None.

        # Example:
        columns example:
        .. code-block:: python
            border = "border-2 border-gray-200"

            with ui.grid(columns=2).classes("h-[200px]").classes(border) as g:

                # a in the first row and first column
                html.paragraph("a value").classes(border)
                # b in the first row and second column
                html.paragraph("b value").classes(border)

                # c in the second row and span over 2 columns
                html.paragraph("c value").use(
                    g.mark_area_position(column_span=2)
                ).classes(border)

        template areas example:
        .. code-block:: python
            border = "border-2 border-gray-200"

            template = r"""
            "a b c" 1fr
            "a b ." 2fr / 1fr 1fr 2fr
            """

            with ui.grid(template=template).classes("h-[200px]").classes(border) as g:
                html.paragraph("a value").use(g.mark_area("a")).classes(border)
                html.paragraph("b value").use(g.mark_area("b")).classes(border)
                html.paragraph("c value").use(g.mark_area("c")).classes(border)
        '''

        super().__init__("div")
        self.style("display: grid;")

        if rows is not None:
            if isinstance(rows, int):
                rows = f"repeat({rows}, 1fr)"

            if isinstance(rows, ObservableMixin):
                rows = _convert_to_repeat_computed(rows)

            self.style({"grid-template-rows": rows})

        if columns is not None:
            if isinstance(columns, int):
                columns = f"repeat({columns}, 1fr)"

            if isinstance(columns, ObservableMixin):
                columns = _convert_to_repeat_computed(columns)

            self.style({"grid-template-columns": columns})

        if template is not None:
            self.style({"grid-template": template})

    def mark_area(self, area: TMaybeRef[str]):
        """Marks an area in the grid

        Args:
            area (TMaybeRef[str]): Area name

        """

        def use_fn(element: Element):
            element.style({"grid-area": area})

        return use_fn

    def mark_area_position(
        self,
        *,
        row: Optional[int] = None,
        column: Optional[int] = None,
        row_span: Optional[int] = None,
        column_span: Optional[int] = None,
    ):
        """Marks an area in the grid with position

        Args:
            row (Optional[int], optional): Start position of row, 1-based. Defaults to None.
            column (Optional[int], optional): Start position of column, 1-based. Defaults to None.
            row_span (Optional[int], optional): The span value at the end of the row. Defaults to None.
            column_span (Optional[int], optional): The span value at the end of the column. Defaults to None.
        """
        real_row = "auto" if row is None else row
        real_column = "auto" if column is None else column
        real_row_span = "auto" if row_span is None else f"span {row_span}"
        real_column_span = "auto" if column_span is None else f"span {column_span}"

        area = f"{real_row} / {real_column} / {real_row_span} / {real_column_span}"
        return self.mark_area(area)

    @staticmethod
    def auto_columns(
        *,
        min_width: TMaybeRef[str],
        mode: TMaybeRef[Literal["auto-fill", "auto-fit"]] = "auto-fit",
    ):
        """
        Generate a dynamic grid column configuration for responsive layout systems.

        Creates a computed layout specification that calculates column dimensions
        based on minimum width requirements and auto-sizing behavior. Retu

        Args:
            min_width (TMaybeRef[str]):
                Minimum width constraint for columns as a CSS length string (e.g., "300px").
                Accepts reactive references for dynamic updates.
            mode (TMaybeRef[Literal[&quot;auto, optional):
                Auto-sizing behavior strategy:
                - "auto-fill": Preserves container space by creating additional columns
                - "auto-fit": Adjusts columns to fit available space.
                Defaults to "auto-fit".

        Example:
        .. code-block:: python

            with ui.grid(columns=ui.grid.auto_columns(min_width="300px")):
                ...
        """
        template = JsComputed(
            inputs=[min_width, mode],
            code=r"(min_width, mode)=> `repeat(${mode}, minmax(min(${min_width},100%), 1fr))`",
        )

        return template

    @staticmethod
    def auto_rows(
        *,
        min_height: TMaybeRef[str],
        mode: TMaybeRef[Literal["auto-fill", "auto-fit"]] = "auto-fit",
    ):
        """
        Generate a dynamic grid row configuration for responsive layout systems.

        Creates a computed layout specification that calculates row dimensions
        based on minimum height requirements and auto-sizing behavior.

        Args:
            min_height (TMaybeRef[str]):
                Minimum height constraint for rows as a CSS length string (e.g., "300px").
            mode (TMaybeRef[Literal[&quot;auto, optional):
                Auto-sizing behavior strategy:
                - "auto-fill": Preserves container space by creating additional rows
                - "auto-fit": Adjusts rows to fit available space.
                Defaults to "auto-fit".

        Example:
        .. code-block:: python

            with ui.grid(rows=ui.grid.auto_rows(min_height="300px")):
                ...
        """

        template = JsComputed(
            inputs=[min_height, mode],
            code=r"(min_height, mode)=> `repeat(${mode}, minmax(min(${min_height},100%), 1fr))`",
        )

        return template

    def row_gap(self, gap: TMaybeRef[str]) -> Grid:
        return self.style({"row-gap": gap})

    def column_gap(self, gap: TMaybeRef[str]) -> Grid:
        return self.style({"column-gap": gap})

    def gap(self, gap: TMaybeRef[str]) -> Grid:
        return self.row_gap(gap).column_gap(gap)


def _convert_to_repeat_computed(value: ObservableMixin):
    return JsComputed(
        inputs=[value],
        code=r"""(value)=> {
    if (typeof value === "number"){
        return `repeat(${value}, 1fr)`
    }
    return value                     
    }""",
    )
