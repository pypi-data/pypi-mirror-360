from typing import Union, Any
from .observable import ObservableMixin
from .py_binding import CanInputMixin

TObservableInput = Union[ObservableMixin, CanInputMixin, Any]
