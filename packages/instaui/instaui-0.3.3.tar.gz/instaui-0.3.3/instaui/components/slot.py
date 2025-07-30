from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional
from instaui.common.jsonable import Jsonable
from instaui.runtime import get_slot_stacks, pop_slot
from instaui.runtime._app import ready_scope
from instaui.vars.slot_prop import BindingSlotPropItem

if TYPE_CHECKING:
    from instaui.components.component import Component

_DEFAULT_SLOT_NAME = ":"


class SlotManager(Jsonable):
    def __init__(self) -> None:
        super().__init__()
        self._slots: Dict[str, Slot] = {}

    def get_slot(self, name: str) -> Slot:
        name = _DEFAULT_SLOT_NAME if name == "default" else name

        if name not in self._slots:
            self._slots[name] = Slot(name)

        return self._slots[name]

    @property
    def default(self):
        return self.get_slot(_DEFAULT_SLOT_NAME)

    def _to_json_dict(self):
        return {name: slot._to_json_dict() for name, slot in self._slots.items()}

    def has_slot(self) -> bool:
        return len(self._slots) > 0 and any(
            slot._children for slot in self._slots.values()
        )


class Slot(Jsonable):
    def __init__(self, name: str) -> None:
        super().__init__()

        self._id: Optional[str] = None
        self._name = name
        self._children: List[Component] = []
        self._use_slot_props: bool = False
        self._scope_wrapper = ready_scope()
        self._slot_prop_info = SlotPropInfo(self._scope_wrapper)

    def slot_props(self, name: str):
        self._use_slot_props = True
        self._slot_prop_info.setup()

        item = BindingSlotPropItem(
            name, self._slot_prop_info.sid, self._slot_prop_info.var_id
        )

        return item[name]

    def __getitem__(self, item: str):
        return self.slot_props(item)

    def __enter__(self):
        get_slot_stacks().append(self)
        self._scope_wrapper.enter()

        return self

    def __exit__(self, *_):
        self._scope_wrapper.exit()
        pop_slot()

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._children:
            data["items"] = self._children

        if self._use_slot_props:
            data["use_prop"] = 1

        if self._scope_wrapper.used and self._scope_wrapper.scope.has_registered_task:
            data["sid"] = self._scope_wrapper.scope_id

        return data

    def _to_items_container_config(self) -> Dict:
        data = self._to_json_dict()

        return {k: v for k, v in data.items() if k in ("items", "sid")}


class SlotPropInfo(Jsonable):
    def __init__(self, scope_wrapper: ready_scope):
        pass

        self._scope_wrapper = scope_wrapper
        self.__register_info = None

    def setup(self):
        if self.__register_info is not None:
            return
        scope = self._scope_wrapper.scope
        self.__register_info = scope.register_slot_prop_info_task(self)

    @property
    def sid(self) -> str:
        return self.__register_info.scope_id  # type: ignore

    @property
    def var_id(self) -> str:
        return self.__register_info.var_id  # type: ignore

    def _to_json_dict(self):
        return {
            "sid": self.sid,
            "id": self.var_id,
        }
