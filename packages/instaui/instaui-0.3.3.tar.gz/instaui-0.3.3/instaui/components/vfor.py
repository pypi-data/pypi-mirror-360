from __future__ import annotations
from typing import (
    Dict,
    Literal,
    Optional,
    Union,
    Sequence,
    Generic,
    TypeVar,
    cast,
    overload,
)
from enum import Enum

from instaui.components.component import Component
from instaui.vars.vfor_item import VForItem

from instaui.vars.mixin_types.element_binding import (
    ElementBindingMixin,
    ElementBindingProtocol,
)

_T = TypeVar("_T")


class VForArrayTypeEnum(Enum):
    CONST = "c"
    REF = "r"
    RANGE = "n"


class VFor(Component, Generic[_T]):
    def __init__(
        self,
        data: Union[Sequence[_T], ElementBindingProtocol, Dict[str, _T], _T],
        *,
        key: Union[Literal["item", "index"], str] = "index",
    ):
        """for loop component.

        Args:
            data (Union[Sequence[_T], ElementBindingMixin[List[_T]]]): data source.
            key (Union[Literal[&quot;item&quot;, &quot;index&quot;], str]]): key for each item. Defaults to 'index'.

        Examples:
        .. code-block:: python
            items = ui.state([1,2,3])

            with ui.vfor(items) as item:
                html.span(item)

            # object key
            items = ui.state([{"name": "Alice", "age": 20}, {"name": "Bob", "age": 30}])
            with ui.vfor(items, key=":item=>item.name") as item:
                html.span(item.name)
        """

        super().__init__("vfor")
        self._data = data
        self._key = key
        self._num = None
        self._transition_group_setting = None

    def __enter__(self) -> _T:
        super().__enter__()
        return cast(_T, VForItem())

    def _set_num(self, num):
        self._num = num

    def transition_group(self, name="fade", tag: Optional[str] = None):
        self._transition_group_setting = {"name": name, "tag": tag}
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._key is not None and self._key != "index":
            data["fkey"] = self._key

        if self._data is not None or self._num is not None:
            array_type = (
                VForArrayTypeEnum.REF
                if isinstance(self._data, ElementBindingMixin)
                else VForArrayTypeEnum.RANGE
                if self._num is not None
                else VForArrayTypeEnum.CONST
            )

            array_value = (
                self._data._to_element_binding_config()
                if isinstance(self._data, ElementBindingMixin)
                else self._num
                if self._num is not None
                else self._data
            )

            data["array"] = {"type": array_type, "value": array_value}

        if self._transition_group_setting is not None:
            data["tsGroup"] = {
                k: v for k, v in self._transition_group_setting.items() if v is not None
            }

        if self._slot_manager.has_slot():
            slot_data = self._slot_manager.get_slot(
                "default"
            )._to_items_container_config()
            data.update(slot_data)

        return data

    @overload
    @classmethod
    def range(cls, end: int) -> VFor[int]: ...

    @overload
    @classmethod
    def range(cls, end: ElementBindingProtocol) -> VFor[int]: ...

    @classmethod
    def range(cls, end: Union[int, ElementBindingProtocol]) -> VFor[int]:
        obj = cls(None)  # type: ignore

        num = (  # type: ignore
            end._to_element_binding_config()
            if isinstance(end, ElementBindingMixin)
            else end
        )

        obj._set_num(num)

        return obj  # type: ignore


def iter_info(item: _T) -> VForItem[_T]:
    return cast(VForItem[_T], item)
