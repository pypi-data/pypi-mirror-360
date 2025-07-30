from typing import List, Optional
from instaui.common.jsonable import Jsonable
from instaui.vars._types import OutputSetType
from instaui.vars.mixin_types.py_binding import CanOutputMixin
from pydantic import BaseModel


class RouterOutput(Jsonable, CanOutputMixin):
    def __init__(self):
        self.type = "routeAct"

    def _to_output_config(self):
        return {}

    def _to_json_dict(self):
        data = super()._to_json_dict()

        return data

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.RouterAction


class RouterMethod(BaseModel):
    fn: str
    args: Optional[List]
