from __future__ import annotations

from typing import (
    Dict,
    Optional,
    Union,
)
from instaui.common.jsonable import Jsonable
from instaui.runtime import (
    get_app_slot,
    check_default_app_slot_or_error,
)
from instaui.components.slot import SlotManager
from instaui.vars.mixin_types.element_binding import (
    ElementBindingMixin,
    ElementBindingProtocol,
)


class Component(Jsonable):
    def __init__(self, tag: Optional[Union[str, ElementBindingProtocol]] = None):
        check_default_app_slot_or_error(
            "Not allowed to create element outside of ui.page"
        )

        self._tag = (
            "div"
            if tag is None or tag == ""
            else (
                tag._to_element_binding_config()
                if isinstance(tag, ElementBindingMixin)
                else str(tag)
            )
        )
        self._slot_manager = SlotManager()

        get_app_slot().append_component_to_container(self)

    def __enter__(self):
        self._slot_manager.default.__enter__()
        return self

    def __exit__(self, *_) -> None:
        self._slot_manager.default.__exit__(*_)

    def _to_json_dict(self) -> Dict:
        data: Dict = {
            "tag": self._tag,
        }

        return data
