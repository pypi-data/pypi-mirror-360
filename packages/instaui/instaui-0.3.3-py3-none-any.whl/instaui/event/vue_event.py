import typing
from instaui.common.jsonable import Jsonable
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.vars._types import InputBindingType
from .event_mixin import EventMixin


class VueEvent(Jsonable, EventMixin):
    """
    Create an event object that can be bound to a UI component's event listener.

    This function generates a callable event handler with optional contextual bindings.
    The event logic is defined via a code string, which can reference bound variables.

    Args:
        code (str): A string containing the executable logic for the event handler.
                    Typically contains a function body or expression that utilizes bound variables.
        bindings (typing.Optional[typing.Dict[str, typing.Any]], optional): A dictionary mapping variable names to values that should be available in the
            event handler's context. If None, no additional bindings are created.. Defaults to None.

    Example:
    .. code-block:: python
        a = ui.state(1)

        event = ui.vue_event(bindings={"a": a}, code=r'''()=> { a.value +=1}''')

        html.span(a)
        html.button("plus").on("click", event)
    """

    def __init__(
        self,
        *,
        code: str,
        bindings: typing.Optional[typing.Dict[str, typing.Any]] = None,
    ):
        self.code = code
        self._bindings = bindings

    def copy_with_extends(self, extends: typing.Dict):
        raise NotImplementedError("VueEvent does not support extends")

    def event_type(self):
        return "vue"

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["type"] = self.event_type()
        if self._bindings:
            data["inputs"] = {
                name: {
                    "value": v._to_input_config()
                    if isinstance(v, CanInputMixin)
                    else v,
                    "type": v._to_event_input_type().value
                    if isinstance(v, CanInputMixin)
                    else InputBindingType.Data,
                }
                for name, v in self._bindings.items()
            }
        return data


vue_event = VueEvent
