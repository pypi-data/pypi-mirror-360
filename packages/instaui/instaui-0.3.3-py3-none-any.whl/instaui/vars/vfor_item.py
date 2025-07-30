from __future__ import annotations
from typing import Any, Dict, Generic, Tuple, TypeVar, Union, cast

from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.pathable import CanPathPropMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.path_var import PathVar


_T = TypeVar("_T")


class VForItemProxy(
    PathVar,
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    CanPathPropMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
    Jsonable,
    Generic[_T],
):
    def __init__(self, vfor_item: VForItem[_T]):
        self._vfor_item = vfor_item

    def __getattr__(self, name: str):
        return self._vfor_item[name]

    @property
    def __vfor_item_(self):
        return super().__getattribute__("_vfor_item")

    def __getitem__(self, name):
        return self.__vfor_item_[name]

    def _to_element_binding_config(self) -> Dict:
        return self.__vfor_item_._to_element_binding_config()

    def _to_input_config(self):
        return self.__vfor_item_._to_input_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__vfor_item_._to_path_prop_binding_config()

    def _to_output_config(self):
        return self.__vfor_item_._to_output_config()

    def _to_str_format_binding(self, order: int) -> Tuple[str, str]:
        return self.__vfor_item_._to_str_format_binding(order)

    def _to_pathable_binding_config(self) -> Dict:
        return self.__vfor_item_._to_pathable_binding_config()

    def _to_observable_config(self):
        return self.__vfor_item_._to_observable_config()

    def _to_json_dict(self):
        return self.__vfor_item_._to_json_dict()

    def _to_event_output_type(self) -> OutputSetType:
        return self.__vfor_item_._to_event_output_type()

    def _to_event_input_type(self) -> InputBindingType:
        return self.__vfor_item_._to_event_input_type()


class VForItem(
    PathVar,
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    CanPathPropMixin,
    ElementBindingMixin[_T],
    StrFormatBindingMixin,
    Jsonable,
    Generic[_T],
):
    SCOPE_TYPE = "fv"

    def __init__(self):
        super().__init__()
        scope = get_current_scope()
        self.__register_info = scope.register_vfor_item_task(self)

    def __getattr__(self, name: str):
        return self[name]

    # def __getitem__(self, name):
    #     return self[name]

    @property
    def dict_key(self):
        return cast(Any, VForItemKey())

    @property
    def dict_value(self):
        return self

    @property
    def index(self) -> int:
        return cast(int, VForIndex())

    @property
    def value(self) -> _T:
        return cast(_T, self)

    # @property
    # def proxy(self):
    #     return cast(_T, VForItemProxy(self))

    def _to_binding_config(self) -> Union[Jsonable, Dict]:
        return self.__to_binding_config()

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_output_config(self):
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_pathable_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_observable_config(self):
        return self.__to_binding_config()

    def __to_binding_config(self):
        data: Dict = {
            "sid": self.__register_info.scope_id,
            "id": self.__register_info.var_id,
        }

        return data

    def _to_json_dict(self):
        data: Dict = {
            "id": self.__register_info.var_id,
        }

        return data

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref


class VForIndex(
    CanInputMixin,
    CanPathPropMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
    Jsonable,
):
    SCOPE_TYPE = "fi"

    def __init__(self):
        super().__init__()
        scope = get_current_scope()
        self.__register_info = scope.register_vfor_index_task(self)

    def __to_binding_config(self):
        data: Dict = {
            "sid": self.__register_info.scope_id,
            "id": self.__register_info.var_id,
        }

        return data

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_json_dict(self):
        return {
            "id": self.__register_info.var_id,
        }

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref


class VForItemKey(
    CanInputMixin,
    CanPathPropMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
    Jsonable,
):
    SCOPE_TYPE = "fk"

    def __init__(self):
        super().__init__()
        scope = get_current_scope()
        self.__register_info = scope.register_vfor_key_task(self)

    def __to_binding_config(self):
        data: Dict = {
            "sid": self.__register_info.scope_id,
            "id": self.__register_info.var_id,
        }

        return data

    def _to_element_binding_config(self):
        return self.__to_binding_config()

    def _to_input_config(self):
        return self.__to_binding_config()

    def _to_path_prop_binding_config(self) -> Dict:
        return self.__to_binding_config()

    def _to_json_dict(self):
        return {
            "id": self.__register_info.var_id,
        }

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref


# class VForDict(
#     CanInputMixin,
#     CanOutputMixin,
#     StrFormatBindingMixin,
#     ElementBindingMixin,
#     Jsonable,
# ):
#     def __init__(self, vfor: VFor):
#         self._vfor = vfor

#     @property
#     def dict_key(self):
#         return self._vfor.current[0]

#     @property
#     def dict_value(self):
#         return self._vfor.current[1]

#     @contextmanager
#     def with_index(self):
#         self.__enter__()
#         yield self, cast(int, VForIndex(self._vfor))

#     def __enter__(self):
#         self._vfor.__enter__()
#         return self

#     def __exit__(self, *_) -> None:
#         return self._vfor.__exit__(*_)

#     def _to_element_binding_config(self) -> Dict:
#         return self.dict_value._to_element_binding_config()

#     def _to_input_config(self):
#         return self.dict_value._to_input_config()

#     def _to_output_config(self):
#         return self.dict_value._to_output_config()

#     def _to_json_dict(self):
#         return self.dict_value._to_json_dict()

#     def _to_event_output_type(self) -> EventOutputType:
#         raise ValueError("VForDict does not support output events")

#     def _to_event_input_type(self) -> EventInputType:
#         return EventInputType.Ref


# class VForWithIndex(Generic[_T]):
#     def __init__(self, vfor: VFor[_T]):
#         self._vfor = vfor

#     def __enter__(self):
#         self._vfor.__enter__()
#         return cast(_T, self._vfor.current.proxy), cast(int, VForIndex(self._vfor))

#     def __exit__(self, *_) -> None:
#         return self._vfor.__exit__(*_)


TVForItem = VForItem
TVForIndex = VForIndex
