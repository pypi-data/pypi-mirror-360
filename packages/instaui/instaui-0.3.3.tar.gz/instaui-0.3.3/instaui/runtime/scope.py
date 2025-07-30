from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Optional
import functools
import weakref
from instaui.common.jsonable import Jsonable


if TYPE_CHECKING:
    from instaui.vars.mixin_types.var_type import VarMixin
    from instaui.vars.mixin_types.py_binding import CanInputMixin
    from instaui.vars.web_computed import WebComputed
    from instaui.vars.js_computed import JsComputed
    from instaui.vars.vue_computed import VueComputed
    from instaui.vars.data import ConstData
    from instaui.watch.web_watch import WebWatch
    from instaui.watch.js_watch import JsWatch
    from instaui.watch.vue_watch import VueWatch
    from instaui.vars.element_ref import ElementRef
    from instaui.vars.vfor_item import VForItem, VForIndex, VForItemKey
    from instaui.components.slot import SlotPropInfo
    from instaui.js.fn import JsFn


class Scope(Jsonable):
    def __init__(self, id: str) -> None:
        super().__init__()
        self.id = id
        self._vars_id_counter = 0
        self._element_ref_id_counter = 0
        self._refs: List[VarMixin] = []
        self._element_refs: List[ElementRef] = []
        self._const_data: List[ConstData] = []
        self._js_computeds: List[JsComputed] = []
        self._vue_computeds: List[VueComputed] = []
        self._web_computeds: List[WebComputed] = []
        self._run_method_records: List = []
        self._web_watch_configs: List[Dict] = []
        self._js_watch_configs: List[Dict] = []
        self._vue_watch_configs: List[Dict] = []
        self._vfor_item: Optional[VForItem] = None
        self._vfor_item_key: Optional[VForItemKey] = None
        self._vfor_index: Optional[VForIndex] = None
        self._slot_prop_info: Optional[SlotPropInfo] = None
        self._js_fns: List[JsFn] = []
        self._query = {}
        self.__has_registered_task = False

    def _mark_has_registered_task(self):
        self.__has_registered_task = True

    @property
    def has_var(self):
        return self._vars_id_counter > 0

    @property
    def has_registered_task(self):
        return self.__has_registered_task

    def generate_vars_id(self) -> str:
        self._vars_id_counter += 1
        return str(self._vars_id_counter)

    def set_query(self, url: str, key: str, on: List[CanInputMixin]) -> None:
        self._query = {
            "url": url,
            "key": key,
            "on": [v._to_input_config() for v in on],
        }

    def register_web_watch(self, watch: WebWatch) -> None:
        self._mark_has_registered_task()
        self._web_watch_configs.append(watch._to_json_dict())

    def register_js_watch(self, watch: JsWatch) -> None:
        self._mark_has_registered_task()
        self._js_watch_configs.append(watch._to_json_dict())

    def register_vue_watch(self, watch: VueWatch) -> None:
        self._mark_has_registered_task()
        self._vue_watch_configs.append(watch._to_json_dict())

    def register_data_task(self, data: ConstData):
        weak_obj = weakref.ref(data)

        def register_fn():
            self._const_data.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_ref_task(self, ref: VarMixin):
        weak_obj = weakref.ref(ref)

        def register_fn():
            self._refs.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_element_ref_task(self, target: ElementRef):
        weak_obj = weakref.ref(target)

        def register_fn():
            self._element_refs.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_vfor_item_task(self, vfor_item: VForItem):
        weak_obj = weakref.ref(vfor_item)

        def register_fn():
            self._vfor_item = weak_obj()
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_slot_prop_info_task(self, slot_prop_info: SlotPropInfo):
        weak_obj = weakref.ref(slot_prop_info)

        def register_fn():
            self._slot_prop_info = weak_obj()
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_vfor_index_task(self, vfor_index: VForIndex):
        weak_obj = weakref.ref(vfor_index)

        def register_fn():
            self._vfor_index = weak_obj()
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_vfor_key_task(self, vfor_key: VForItemKey):
        weak_obj = weakref.ref(vfor_key)

        def register_fn():
            self._vfor_item_key = weak_obj()
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_js_computed_task(self, computed: JsComputed):
        weak_obj = weakref.ref(computed)

        def register_fn():
            self._js_computeds.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_computed_task(self, computed: WebComputed):
        weak_obj = weakref.ref(computed)

        def register_fn():
            self._web_computeds.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_vue_computed_task(self, computed: VueComputed):
        weak_obj = weakref.ref(computed)

        def register_fn():
            self._vue_computeds.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def register_js_fn_task(self, fn: JsFn):
        weak_obj = weakref.ref(fn)

        def register_fn():
            self._js_fns.append(weak_obj())  # type: ignore
            return self.generate_vars_id()

        return VarRegisterTaskForScope(self, register_fn)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if self._refs:
            data["refs"] = self._refs
        if self._query:
            data["query"] = self._query
        if self._web_watch_configs:
            data["py_watch"] = self._web_watch_configs
        if self._js_watch_configs:
            data["js_watch"] = self._js_watch_configs
        if self._vue_watch_configs:
            data["vue_watch"] = self._vue_watch_configs
        if self._element_refs:
            data["eRefs"] = self._element_refs

        if self._web_computeds:
            data["web_computed"] = self._web_computeds

        if self._js_computeds:
            data["js_computed"] = self._js_computeds

        if self._vue_computeds:
            data["vue_computed"] = self._vue_computeds
        if self._const_data:
            data["data"] = self._const_data

        if self._js_fns:
            data["jsFn"] = self._js_fns

        # vfor info
        vfor_dict = {}
        if self._vfor_item:
            vfor_dict[self._vfor_item.SCOPE_TYPE] = self._vfor_item
        if self._vfor_index:
            vfor_dict[self._vfor_index.SCOPE_TYPE] = self._vfor_index
        if self._vfor_item_key:
            vfor_dict[self._vfor_item_key.SCOPE_TYPE] = self._vfor_item_key

        if vfor_dict:
            data["vfor"] = vfor_dict

        if self._slot_prop_info:
            data["sp"] = self._slot_prop_info._to_json_dict()

        return data


class GlobalScope(Scope):
    def __init__(self, id: str) -> None:
        super().__init__(id)

    def register_ref_task(self, var: VarMixin) -> None:
        raise ValueError("Can not register ref in global scope")

    def register_computed_task(self, computed: WebComputed) -> None:
        raise ValueError("Can not register web_computeds  in global scope")

    def register_js_computed_task(self, computed: JsComputed):
        raise ValueError("Can not register js_computeds  in global scope")

    def register_vue_computed_task(self, computed: VueComputed):
        raise ValueError("Can not register vue_computeds  in global scope")

    def register_web_watch(self, watch: WebWatch) -> None:
        raise ValueError("Can not register web_watchs  in global scope")

    def register_js_watch(self, watch: JsWatch) -> None:
        raise ValueError("Can not register js_watchs  in global scope")

    def register_vue_watch(self, watch: VueWatch) -> None:
        raise ValueError("Can not register vue_watchs  in global scope")


class VarRegisterTaskForScope:
    def __init__(self, scope: Scope, register_fn: Callable[[], str]) -> None:
        scope._mark_has_registered_task()
        self._scope_id = scope.id
        self._id_gen_fn = functools.lru_cache(maxsize=1)(register_fn)

    @property
    def scope_id(self) -> str:
        return self._scope_id

    @property
    def var_id(self) -> str:
        return self._id_gen_fn()
