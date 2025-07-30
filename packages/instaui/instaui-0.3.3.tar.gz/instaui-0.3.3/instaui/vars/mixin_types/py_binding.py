from abc import ABC, abstractmethod
from typing import Sequence
from instaui.vars._types import InputBindingType, OutputSetType


class CanInputMixin(ABC):
    @abstractmethod
    def _to_input_config(self):
        pass

    @abstractmethod
    def _to_event_input_type(self) -> InputBindingType:
        pass


class CanOutputMixin(ABC):
    @abstractmethod
    def _to_output_config(self):
        pass

    @abstractmethod
    def _to_event_output_type(self) -> OutputSetType:
        pass


def inputs_to_config(inputs: Sequence[CanInputMixin]):
    return [
        {
            "value": input._to_input_config()
            if isinstance(input, CanInputMixin)
            else input,
            "type": input._to_event_input_type().value
            if isinstance(input, CanInputMixin)
            else InputBindingType.Data.value,
        }
        for input in inputs
    ]


def outputs_to_config(outputs: Sequence[CanOutputMixin]):
    return [
        {
            "ref": ref._to_output_config(),
            "type": ref._to_event_output_type().value,
        }
        for ref in outputs
    ]


def _assert_outputs_be_can_output_mixin(outputs: Sequence):
    for output in outputs:
        if not isinstance(output, CanOutputMixin):
            raise TypeError("The outputs parameter must be a `ui.state`")
