from __future__ import annotations
from typing import (
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Hashable,
)

_TLinkActionObj = TypeVar("_TLinkActionObj")

_DEFAULT_KEY_FN = lambda x: x  # noqa: E731


class LinkManager(Generic[_TLinkActionObj]):
    def __init__(
        self, key_fn: Optional[Callable[[_TLinkActionObj], Hashable]] = None
    ) -> None:
        self._key_fn = key_fn or _DEFAULT_KEY_FN
        self._actions_map: Dict[
            Tuple[Literal["add", "remove"], Hashable], _TLinkActionObj
        ] = {}

    def add_link(
        self,
        obj: _TLinkActionObj,
    ):
        key = ("add", self._key_fn(obj))
        self._actions_map[key] = obj

    def remove_link(
        self,
        obj: _TLinkActionObj,
    ):
        key = ("remove", self._key_fn(obj))
        self._actions_map[key] = obj

    def get_valid_links(
        self, secondary_manager: Optional[LinkManager] = None
    ) -> List[_TLinkActionObj]:
        secondary_maps = secondary_manager._actions_map if secondary_manager else {}
        merger_map = {**secondary_maps, **self._actions_map}

        result = {}

        for (action, key), obj in merger_map.items():
            if action == "add":
                result[key] = obj
                continue

            if key in result:
                del result[key]

        return list(result.values())


if __name__ == "__main__":

    def test_baes():
        manager: LinkManager[str] = LinkManager()
        manager.add_link("a")
        manager.add_link("b")
        manager.add_link("c")
        manager.remove_link("b")

        assert manager.get_valid_links() == ["a", "c"]

    test_baes()

    def test_with_other():
        other: LinkManager[str] = LinkManager()
        other.add_link("a")
        other.add_link("b")
        other.add_link("c")

        manager1: LinkManager[str] = LinkManager()
        manager1.add_link("b")
        manager1.add_link("d")
        manager1.add_link("e")
        manager1.remove_link("a")
        manager1.remove_link("b")

        assert manager1.get_valid_links(other) == ["c", "d", "e"]

    test_with_other()
