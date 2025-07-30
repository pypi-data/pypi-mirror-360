from typing import Any, Iterable, Sequence, Union
from instaui.common.jsonable import Jsonable


class PatchSetRecord:
    def __init__(self, *, path: Sequence[Union[str, int]], value: Any):
        self.path = list(path)
        self.value = value


class PatchSet(Jsonable):
    def __init__(self, records: Iterable[PatchSetRecord]):
        self._records = list(records)

    def patch_set(self, *, path: Sequence[Union[str, int]], value: Any):
        return PatchSet([*self._records, PatchSetRecord(path=path, value=value)])

    def _to_json_dict(self):
        return [[r.path, r.value] for r in self._records]


def patch_set(*, path: Sequence[Union[str, int]], value: Any):
    """
    Generates a patch to specify how data should be updated.

    This function is typically used within the return value of functions
    used in `ui.event` or `ui.watch`, indicating the way data modifications are applied.

    Args:
        path (Sequence[Union[str, int]]): A sequence representing the path to the item that needs to be updated.
                                           Each element can either be a string (for dictionary keys) or an integer
                                           (for list indices).
        value (Any): The new value to set at the specified path. Can be of any type.

    Example:
    .. code-block:: python

        data = ui.state(
            {
                "v1": ["a", "b", "c"],
                "v2": ["x", "y", "z"],
            }
        )

        @ui.event(outputs=[data])
        def update_data():
            # update the second element of "v1" to "foo"
            return ui.patch_set(path=["v1", 1], value="foo")

        html.button("update data").on_click(update_data)
        ui.label(data)
    """

    return PatchSet([PatchSetRecord(path=path, value=value)])
