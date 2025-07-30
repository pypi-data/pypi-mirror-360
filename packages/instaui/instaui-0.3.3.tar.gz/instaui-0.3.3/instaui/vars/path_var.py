from __future__ import annotations
from abc import abstractmethod
from typing import List, Optional, Union
from typing_extensions import Self
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.pathable import PathableMixin, CanPathPropMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin


class PathVar(PathableMixin):
    def __getitem__(self, item: Union[str, int, CanPathPropMixin]):
        return PathTrackerBindable(self)[item]

    def not_(self):
        return PathTrackerBindable(self).not_()

    def __add__(self, other: str):
        return PathTrackerBindable(self) + other

    def __radd__(self, other: str):
        return other + PathTrackerBindable(self)


class PathTracker:
    def __init__(self, paths: Optional[List[Union[str, List[str]]]] = None):
        self.paths = paths or []

    def __getitem__(self, key) -> Self:
        return self.__new_self__([*self.paths, key])

    def __getattr__(self, key) -> Self:
        return self.__new_self__([*self.paths, key])

    def not_(self) -> Self:
        return self.__new_self__([*self.paths, ["!"]])

    def __add__(self, other: str) -> Self:
        return self.__new_self__([*self.paths, ["+", other]])

    def __radd__(self, other: str) -> Self:
        return self.__new_self__([*self.paths, ["~+", other]])

    @abstractmethod
    def __new_self__(self, paths: List[Union[str, List[str]]]) -> Self:
        pass


class PathTrackerBindable(
    PathTracker,
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
):
    def __init__(self, source: PathableMixin):
        super().__init__()
        self.__source = source

    def __new_self__(self, paths: List[Union[str, List[str]]]) -> PathTrackerBindable:
        obj = PathTrackerBindable(self.__source)
        obj.paths = paths
        return obj

    def _to_element_binding_config(self):
        return self._to_json_dict()

    def _to_input_config(self):
        return self._to_json_dict()

    def _to_output_config(self):
        return self._to_json_dict()

    def _to_observable_config(self):
        return self._to_json_dict()

    def _to_json_dict(self):
        data = self.__source._to_pathable_binding_config()

        if self.paths:
            data["path"] = [
                ["bind", path._to_path_prop_binding_config()]
                if isinstance(path, CanPathPropMixin)
                else path
                for path in self.paths
            ]

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref
