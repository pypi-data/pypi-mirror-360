from __future__ import annotations
from typing import Any, Dict, Protocol, TYPE_CHECKING, Union
from typing_extensions import Self
from instaui.vars.types import TMaybeRef

if TYPE_CHECKING:
    from instaui.components.element import Element


class PropsProtocol(Protocol):
    def props(self, add: Union[str, Dict[str, Any], TMaybeRef]) -> Self: ...


class CanDisabledMixin:
    def disabled(self: PropsProtocol, disabled: TMaybeRef[bool] = True) -> Element:
        return self.props({"disabled": disabled})  # type: ignore
