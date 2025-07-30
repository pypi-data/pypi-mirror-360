from typing import Any, List, Sequence, TypedDict
from enum import IntEnum
from instaui.common.jsonable import Jsonable
from instaui.skip import is_skip_output
from instaui.patch_update import PatchSet


class TResponse(TypedDict, total=False):
    values: List[Any]
    types: Sequence[int]


class ValueType(IntEnum):
    VALUE = 0
    SKIP = 1
    Patch = 2


def response_data(outputs_binding_count: int, result: Any):
    data: TResponse = {}
    if outputs_binding_count > 0:
        if not isinstance(result, tuple):
            result = [result]

        returns_count = len(result)

        # [(value, 1), (value, 0)]
        result_infos = [
            (_try_get_value_from_jsonable(r), convert_type(r)) for r in result
        ]

        if returns_count == 1 and result_infos[0][1] == ValueType.SKIP:
            return data

        # fill missing values with None
        if returns_count < outputs_binding_count:
            result_infos.extend(
                [(None, ValueType.SKIP)] * (outputs_binding_count - returns_count)
            )

        data["values"] = [
            0 if info[1] == ValueType.SKIP else info[0] for info in result_infos
        ]
        types = [info[1] for info in result_infos]

        if sum(types) > 0:
            data["types"] = types

    return data


def convert_type(value: Any):
    if is_skip_output(value):
        return ValueType.SKIP
    if isinstance(value, PatchSet):
        return ValueType.Patch
    return ValueType.VALUE


def _try_get_value_from_jsonable(value: Any) -> Any:
    if isinstance(value, Jsonable):
        return value._to_json_dict()

    return value
