from typing import Tuple
from abc import ABC


class StrFormatBindingMixin(ABC):
    def _to_str_format_binding(self, order: int) -> Tuple[str, str]:
        var_name = f"___ref_var{order}"
        return var_name, f"${{__Vue.toValue({var_name})}}"
