from __future__ import annotations
from typing import cast
from instaui.components.component import Component
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.types import TMaybeRef


class VIf(Component):
    def __init__(self, on: TMaybeRef[bool]):
        super().__init__("vif")
        self._on = cast(ElementBindingMixin, on)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        data["on"] = (
            self._on
            if isinstance(self._on, bool)
            else self._on._to_element_binding_config()
        )

        if self._slot_manager.has_slot():
            slot_data = self._slot_manager.get_slot(
                "default"
            )._to_items_container_config()
            data.update(slot_data)

        return data
