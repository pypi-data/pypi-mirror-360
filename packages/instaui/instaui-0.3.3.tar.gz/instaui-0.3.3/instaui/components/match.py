from __future__ import annotations

import typing
from instaui.components.component import Component

from instaui.vars.mixin_types.element_binding import ElementBindingProtocol


class Match(Component):
    def __init__(self, on: ElementBindingProtocol):
        super().__init__("match")
        self._on = on
        self.cass_id_count = -1
        self._case_values = []

    def case(self, value: typing.Any):
        self.cass_id_count += 1
        self._case_values.append(value)
        return self._slot_manager.get_slot(str(self.cass_id_count))

    def default(self):
        return self._slot_manager.get_slot(":default")

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["on"] = self._on._to_element_binding_config()
        data["caseValues"] = self._case_values

        data["slots"] = {
            name: slot
            for name, slot in self._slot_manager._slots.items()
            if name != ":"
        }

        default_slot = self._slot_manager.get_slot(
            "default"
        )._to_items_container_config()

        if "sid" in default_slot:
            data["sid"] = default_slot["sid"]

        return data
