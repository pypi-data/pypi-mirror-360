from __future__ import annotations
from typing import Any, Dict
from instaui.components.component import Component
from instaui.vars.types import TMaybeRef
from instaui.vars.mixin_types.element_binding import ElementBindingMixin


class Content(Component):
    def __init__(self, content: TMaybeRef[Any]):
        """Content to be displayed on the page, typically used for pure text content within slots.

        Args:
            content (TMaybeRef[Any]): The textual content to display.

        Examples:
        .. code-block:: python
            with html.div():
                ui.content("Hello, world!")
        """
        super().__init__("content")
        self._content = content

    def _to_json_dict(self) -> Dict:
        data = super()._to_json_dict()
        props = {}
        data["props"] = props

        if isinstance(self._content, ElementBindingMixin):
            props["content"] = self._content._to_element_binding_config()
            props["r"] = 1
        else:
            props["content"] = self._content

        return data
