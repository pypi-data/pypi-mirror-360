import typing
from instaui.vars._types import InputBindingType
from instaui.vars.mixin_types.py_binding import CanInputMixin


class InputSilentData(CanInputMixin):
    def __init__(self, value: typing.Union[CanInputMixin, typing.Any]) -> None:
        self.value = value

    def is_const_value(self) -> bool:
        return not isinstance(self.value, CanInputMixin)

    def _to_input_config(self):
        if isinstance(self.value, CanInputMixin):
            return self.value._to_input_config()
        else:
            return self.value

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref
