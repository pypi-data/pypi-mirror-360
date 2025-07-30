import typing
from . import _types
from . import _utils

from instaui.common.jsonable import Jsonable
from instaui.runtime._app import get_current_scope

from instaui.vars.mixin_types.py_binding import CanOutputMixin, outputs_to_config
from instaui.vars.mixin_types.common_type import TObservableInput
from instaui._helper import observable_helper


class JsWatch(Jsonable):
    def __init__(
        self,
        code: str,
        inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
        outputs: typing.Optional[typing.Sequence[CanOutputMixin]] = None,
        immediate: bool = True,
        deep: typing.Union[bool, int] = False,
        once: bool = False,
        flush: typing.Optional[_types.TFlush] = None,
    ) -> None:
        inputs = observable_helper.auto_made_inputs_to_slient(inputs, outputs)

        self.code = code

        self._inputs, self._is_slient_inputs, self._is_data = (
            observable_helper.analyze_observable_inputs(list(inputs or []))
        )
        self._outputs = [output for output in outputs or []]

        if immediate is not True:
            self.immediate = immediate

        if deep is not False:
            _utils.assert_deep(deep)
            self.deep = deep

        if once is not False:
            self.once = once

        if flush is not None:
            self.flush = flush

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._inputs:
            data["inputs"] = self._inputs

        if sum(self._is_slient_inputs) > 0:
            data["slient"] = self._is_slient_inputs

        if sum(self._is_data) > 0:
            data["data"] = self._is_data

        if self._outputs:
            data["outputs"] = outputs_to_config(self._outputs)

        return data


def js_watch(
    *,
    inputs: typing.Optional[typing.Sequence] = None,
    outputs: typing.Optional[typing.Sequence] = None,
    code: str,
    immediate: bool = True,
    deep: typing.Union[bool, int] = False,
    once: bool = False,
    flush: typing.Optional[_types.TFlush] = None,
):
    """
    Creates a client-side observer that executes JavaScript code in response to reactive source changes.

    Args:
        inputs (typing.Optional[typing.Sequence], optional): Reactive sources to observe. Changes to these sources
                                   trigger the watcher's JavaScript execution.
        outputs (typing.Optional[typing.Sequence], optional): Output targets associated with this watcher. Used for
                                    coordination with other observers.
        code (str, optional): JavaScript code to execute when changes are detected. The code has access
                  to the current values of observed inputs through the `args` parameter.
        immediate (bool, optional):If True, executes the watcher immediately after creation with current values. Defaults to True.
        deep (typing.Union[bool, int], optional): Controls depth of change detection:
                               - True: Recursively tracks nested properties
                               - False: Shallow comparison only
                               - int: Maximum depth level to track (for complex objects).
                               Defaults to False.
        once (bool, optional): If True, automatically stops observation after first trigger. Defaults to False.
        flush (typing.Optional[_types.TFlush], optional): Controls when to flush updates:
                                      - 'sync': Execute immediately on change
                                      - 'post': Batch updates and execute after current tick
                                      - 'pre': Execute before render phase (if applicable)

    # Example:
    .. code-block:: python
        from instaui import ui, html

        num = ui.state(0)
        msg = ui.state('')
        ui.js_watch(inputs=[num], outputs=[msg], code="num => `The number is ${num}`")

        html.number(num)
        ui.label(msg)
    """

    watch = JsWatch(code, inputs, outputs, immediate, deep, once, flush)
    get_current_scope().register_js_watch(watch)
    return watch
