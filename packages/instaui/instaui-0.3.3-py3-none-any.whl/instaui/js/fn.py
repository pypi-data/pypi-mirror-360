from instaui.common.jsonable import Jsonable
from instaui.vars._types import InputBindingType
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.runtime._app import get_app_slot, get_current_scope


class JsFn(Jsonable, CanInputMixin):
    """
    Creates a JavaScript function object from a raw code string.
    Valid targets include: `js_computed`, `js_watch`, and similar JS-bound methods.

    Args:
        code (str): Valid JavaScript function definition string.

    Example:
    .. code-block:: python
        a = ui.state(1)
        add = ui.js_fn(code="(a,b)=> a+b ")
        result = ui.js_computed(inputs=[add, a], code="(add,a)=>  add(a,10) ")

        html.number(a)
        ui.label(result)
    """

    def __init__(self, code: str, *, execute_immediately=False, global_scope=False):
        self.code = code

        scope = get_app_slot().top_scope if global_scope else get_current_scope()
        self.__register_info = scope.register_js_fn_task(self)

        self._execute_immediately = execute_immediately

    def _to_input_config(self):
        return {
            "sid": self.__register_info.scope_id,
            "id": self.__register_info.var_id,
        }

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__register_info.var_id

        if self._execute_immediately is True:
            data["immediately"] = 1

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.JsFn
