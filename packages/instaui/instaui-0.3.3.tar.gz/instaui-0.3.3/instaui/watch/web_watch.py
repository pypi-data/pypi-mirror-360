from __future__ import annotations
import inspect
import typing
from typing_extensions import ParamSpec
from . import _types
from . import _utils

from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_app_slot, get_current_scope
from instaui.handlers import watch_handler

from instaui.vars.mixin_types.py_binding import (
    CanOutputMixin,
    outputs_to_config,
    _assert_outputs_be_can_output_mixin,
)
from instaui.vars.mixin_types.common_type import TObservableInput
from instaui._helper import observable_helper
from instaui import pre_setup as _pre_setup

_SYNC_TYPE = "sync"
_ASYNC_TYPE = "async"

P = ParamSpec("P")
R = typing.TypeVar("R")


class WebWatch(Jsonable, typing.Generic[P, R]):
    def __init__(
        self,
        func: typing.Callable[P, R],
        inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
        outputs: typing.Optional[typing.Sequence[CanOutputMixin]] = None,
        immediate: bool = True,
        deep: typing.Union[bool, int] = True,
        once: bool = False,
        flush: typing.Optional[_types.TFlush] = None,
        pre_setup: typing.Optional[typing.Dict] = None,
        _debug: typing.Optional[typing.Any] = None,
    ) -> None:
        if pre_setup:
            _pre_setup._check_args(pre_setup)

        outputs = [] if outputs is None else outputs

        _assert_outputs_be_can_output_mixin(outputs)

        inputs = observable_helper.auto_made_inputs_to_slient(inputs, outputs)

        self._inputs, self._is_slient_inputs, self._is_data = (
            observable_helper.analyze_observable_inputs(list(inputs or []))
        )

        self._outputs = outputs
        self._fn = func
        self._immediate = immediate
        self._deep = deep
        self._once = once
        self._flush = flush
        self._debug = _debug
        self._pre_setup = pre_setup

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._fn(*args, **kwargs)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        app = get_app_slot()

        if app.mode == "web":
            hkey = watch_handler.create_handler_key(
                page_path=app.page_path,
                handler=self._fn,
            )

            watch_handler.register_handler(hkey, self._fn, len(self._outputs))

            data["fType"] = (
                _ASYNC_TYPE if inspect.iscoroutinefunction(self._fn) else _SYNC_TYPE
            )
            data["key"] = hkey
            if self._inputs:
                data["inputs"] = self._inputs

            if sum(self._is_slient_inputs) > 0:
                data["slient"] = self._is_slient_inputs

            if sum(self._is_data) > 0:
                data["data"] = self._is_data

            if self._debug:
                data["debug"] = self._debug

            if self._outputs:
                data["outputs"] = outputs_to_config(self._outputs)

            if self._immediate is not True:
                data["immediate"] = self._immediate

            if self._deep is not True:
                _utils.assert_deep(self._deep)
                data["deep"] = self._deep
            if self._once is not False:
                data["once"] = self._once
            if self._flush is not None:
                data["flush"] = self._flush
            if self._pre_setup:
                data["preSetup"] = _pre_setup.convert_config(self._pre_setup)

            return data

        return {}


def watch(
    *,
    inputs: typing.Optional[typing.Sequence] = None,
    outputs: typing.Optional[typing.Sequence] = None,
    immediate: bool = True,
    deep: typing.Union[bool, int] = True,
    once: bool = False,
    flush: typing.Optional[_types.TFlush] = None,
    pre_setup: typing.Optional[typing.Dict] = None,
    _debug: typing.Optional[typing.Any] = None,
):
    """
    Creates an observer that tracks changes in reactive sources and triggers callbacks.

    Args:
        inputs (typing.Optional[typing.Sequence], optional): Reactive sources to observe (state objects or computed properties).
                                   Changes to these sources trigger the watcher callback.
        outputs (typing.Optional[typing.Sequence], optional): Output targets associated with this watcher.
                                    Used for coordination with computed properties or other observers.
        immediate (bool, optional): If True, executes callback immediately after creation with current values. Defaults to True.
        deep (typing.Union[bool, int], optional): Controls depth of change detection:
                               - True: Recursively tracks nested properties
                               - False: Shallow comparison only
                               - int: Maximum depth level to track (for complex objects).
                               Defaults to True.
        once (bool, optional):  If True, automatically stops observation after first trigger. Defaults to False.
        flush (typing.Optional[_types.TFlush], optional): Controls when to flush updates:
                                      - 'sync': Execute immediately on change
                                      - 'post': Batch updates and execute after current tick
                                      - 'pre': Execute before render phase (if applicable)
        pre_setup (typing.Optional[typing.Dict], optional): A dictionary of pre-setup actions to be executed before the event executes.


    # Example:
    .. code-block:: python
        from instaui import ui, html

        num = ui.state(0)
        msg = ui.state('')

        @ui.watch(inputs=[num], outputs=[msg])
        def when_num_change(num):
            return f"The number is {num}"

        html.number(num)
        ui.label(msg)

    list append:
    .. code-block:: python
        from instaui import ui, html

        num = ui.state(0)
        msg = ui.state([])

        @ui.watch(inputs=[num, msg], outputs=[msg])
        def when_num_change(num, msg:list):
            msg.append(f"The number changed to {num}")
            return msg

        html.number(num)
        ui.label(msg)

    """

    def wrapper(func: typing.Callable[P, R]):
        obj = WebWatch(
            func,
            inputs,
            outputs=outputs,
            immediate=immediate,
            deep=deep,
            once=once,
            flush=flush,
            pre_setup=pre_setup,
            _debug=_debug,
        )

        get_current_scope().register_web_watch(obj)

    return wrapper
