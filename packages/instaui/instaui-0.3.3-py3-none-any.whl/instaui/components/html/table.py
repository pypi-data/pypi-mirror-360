from __future__ import annotations
from typing import TYPE_CHECKING, Any, List, Union
from instaui.components.element import Element
from instaui.components.content import Content
from instaui.components.vfor import VFor

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Table(Element):
    def __init__(
        self,
        columns: Union[List[str], TMaybeRef[List[str]], None] = None,
        rows: Union[List[List[Any]], TMaybeRef[List[List[Any]]], None] = None,
    ):
        """Create a table element.

        Args:
            columns (Union[List[str], TMaybeRef[List[str]], None], optional): A list of column headers or a reactive reference to such a list. Defaults to None.
            rows (Union[List[List[Any]], TMaybeRef[List[List[Any]]], None], optional): A list of row data, where each row is a list of cell values, or a reactive reference to such a list. Defaults to None.
        """
        super().__init__("table")

        with self:
            with Element("thead"), Element("tr"):
                with VFor(columns) as col:  # type: ignore
                    with Element("th"):
                        Content(col)

            with Element("tbody"):
                with VFor(rows) as row:  # type: ignore
                    with Element("tr"):
                        with VFor(row) as cell:  # type: ignore
                            with Element("td"):
                                Content(cell)
