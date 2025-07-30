from __future__ import annotations
import typing

from instaui.common.jsonable import Jsonable
from instaui.vars.path_var import PathVar

from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.pathable import CanPathPropMixin


class RouteParamsVar(
    Jsonable,
    PathVar,
    ObservableMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
):
    VAR_TYPE = "rp"

    def __init__(
        self,
        prop: typing.Literal["params", "path", "fullPath"] = "params",
    ) -> None:
        super().__init__()
        self._prop = prop

    def __to_binding_config(self):
        return {"type": "rp", "prop": self._prop}

    def _to_pathable_binding_config(self) -> typing.Dict:
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> typing.Dict:
        return self.__to_binding_config()

    def _to_observable_config(self):
        return self.__to_binding_config()

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_json_dict(self):
        raise NotImplementedError("RouteParamsVar is not json serializable")
