from __future__ import annotations
from typing import (
    Any,
    Dict,
    Optional,
    Sequence,
    Union,
    cast,
)

from instaui.vars.mixin_types.observable import ObservableMixin

from . import _types
from . import _utils

from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope


class VueWatch(Jsonable):
    def __init__(
        self,
        sources: Union[Any, Sequence],
        callback: str,
        *,
        bindings: Optional[Dict[str, Any]] = None,
        immediate: bool = False,
        deep: Union[bool, int] = False,
        once: bool = False,
        flush: Optional[_types.TFlush] = None,
    ) -> None:
        self.code = callback

        if not isinstance(sources, Sequence):
            sources = [sources]

        onData = [int(not isinstance(varObj, ObservableMixin)) for varObj in sources]

        if sum(onData) > 0:
            self.onData = onData

        self.on = [
            cast(ObservableMixin, varObj)._to_observable_config()
            if isinstance(varObj, ObservableMixin)
            else varObj
            for varObj in sources
        ]

        if bindings:
            bindData = [
                int(not isinstance(v, ObservableMixin)) for v in bindings.values()
            ]

            if sum(bindData) > 0:
                self.bindData = bindData

            self.bind = {
                k: cast(ObservableMixin, v)._to_observable_config()
                if isinstance(v, ObservableMixin)
                else v
                for k, v in bindings.items()
            }

        if immediate is not False:
            self.immediate = immediate

        if deep is not False:
            _utils.assert_deep(deep)
            self.deep = deep

        if once is not False:
            self.once = once

        if flush is not None:
            self.flush = flush


def vue_watch(
    sources: Union[Any, Sequence],
    callback: str,
    *,
    bindings: Optional[Dict[str, Any]] = None,
    immediate: bool = False,
    deep: Union[bool, int] = False,
    once: bool = False,
    flush: Optional[_types.TFlush] = None,
):
    """ """

    watch = VueWatch(
        sources,
        callback,
        bindings=bindings,
        immediate=immediate,
        deep=deep,
        once=once,
        flush=flush,
    )
    get_current_scope().register_vue_watch(watch)
    return watch
