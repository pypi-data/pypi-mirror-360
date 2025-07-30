from __future__ import annotations

from typing import (
    Any,
    List,
    Optional,
)
from instaui.common.jsonable import Jsonable
from instaui.vars.mixin_types.element_binding import ElementBindingMixin


class Directive(Jsonable):
    def __init__(
        self,
        *,
        is_sys: bool,
        name: str,
        arg: Optional[str] = None,
        modifiers: Optional[List[Any]] = None,
        value: Optional[Any] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self._arg = arg
        self._is_sys = is_sys
        self._modifiers = modifiers
        self._value = value

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Directive):
            return False
        return self.name == other.name

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._arg:
            data["arg"] = self._arg

        if self._value:
            data["value"] = (
                self._value._to_element_binding_config()
                if isinstance(self._value, ElementBindingMixin)
                else self._value
            )

        if self._modifiers:
            data["mf"] = list(dict.fromkeys(self._modifiers).keys())

        data["sys"] = int(self._is_sys)

        return data
