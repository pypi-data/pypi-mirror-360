from __future__ import annotations
from enum import IntEnum
from typing import Literal, TypeVar


_T_Value = TypeVar("_T_Value")
_T_Output_Value = TypeVar("_T_Output_Value", covariant=True)
_T_VAR_TYPE = Literal["ref", "computed", "webComputed"]
_T_Bindable_Type = Literal["ref", "computed", "js", "webComputed", "vforItem"]


class InputBindingType(IntEnum):
    Ref = 0
    EventContext = 1
    Data = 2
    JsFn = 3


class OutputSetType(IntEnum):
    Ref = 0
    RouterAction = 1
    ElementRefAction = 2
