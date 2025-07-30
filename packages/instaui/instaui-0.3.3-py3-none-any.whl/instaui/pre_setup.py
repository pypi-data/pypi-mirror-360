from typing import Dict, Sequence, cast
from instaui.common.jsonable import Jsonable
from instaui.vars.mixin_types.py_binding import CanOutputMixin, CanInputMixin


def _check_args(config: Dict):
    for key in config.keys():
        if not isinstance(key, CanOutputMixin):
            raise TypeError(f"key {key} is not a CanOutputMixin")


def convert_config(config: Dict):
    return [
        {
            "target": cast(CanInputMixin, key)._to_input_config(),
            **value._to_json_dict(),
        }
        if isinstance(value, PreSetupAction)
        else {
            "type": "const",
            "target": cast(CanInputMixin, key)._to_input_config(),
            "value": value,
        }
        for key, value in config.items()
    ]


class PreSetupAction(Jsonable):
    def __init__(self, *, inputs: Sequence, code: str, reset: bool = True):
        self.type = "action"
        self._inputs = inputs
        self.code = code
        self.reset = reset

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if self._inputs:
            data["inputs"] = [
                binding._to_input_config()
                if isinstance(binding, CanInputMixin)
                else binding
                for binding in self._inputs
            ]

        return data
