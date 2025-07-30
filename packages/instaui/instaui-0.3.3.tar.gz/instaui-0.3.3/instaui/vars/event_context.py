from typing import Dict
from instaui.common.jsonable import Jsonable
from instaui.vars._types import InputBindingType
from instaui.vars.mixin_types.py_binding import CanInputMixin


class EventContext(Jsonable, CanInputMixin):
    def __init__(self, path: str):
        self.path = path

    def _to_input_config(self):
        return self._to_binding_config()

    def _to_binding_config(self) -> Dict:
        return {
            "path": self.path,
        }

    @staticmethod
    def dataset(name="eventData"):
        return DatasetEventContext(EventContext(f":e=> e.target.dataset.{name}"))

    @staticmethod
    def args():
        return EventContext(":(...e)=> e")

    @staticmethod
    def e():
        return EventContext(":e => e")

    @staticmethod
    def target_value():
        return EventContext(":e => e.target.value")

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.EventContext


class DatasetEventContext(Jsonable, CanInputMixin):
    def __init__(self, event_context: EventContext) -> None:
        self._event_context = event_context

    def _to_input_config(self):
        return self._to_binding_config()

    def _to_binding_config(self) -> Dict:
        return self._event_context._to_binding_config()

    def _to_json_dict(self):
        return self._event_context._to_json_dict()

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.EventContext
