from importlib import import_module
from types import ModuleType
from typing import Any, Callable, List, Optional
from instaui.runtime.context import get_context


class LazyModule(ModuleType):
    def __init__(
        self,
        name: str,
        member: str,
        *,
        import_error_callback: Optional[Callable[[Exception], None]] = None,
    ):
        super().__init__(name)
        self._name = name
        self._mod = None
        self._member_obj = None
        self._member = member
        self._import_error_callback = import_error_callback

    def __getattr__(self, attr: str) -> Any:
        return self.__try_run(lambda: getattr(self._member_obj, attr))  # type: ignore

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__try_run(lambda: self._member_obj(*args, **kwds))  # type: ignore

    def __dir__(self) -> List[str]:
        if self._mod is None:
            self._mod = import_module(self._name)
        return dir(self._mod)

    def __try_run(self, fn: Callable[..., Any]):
        try:
            self.__try_import()
            return fn()  # type: ignore
        except ImportError as e:
            if get_context().debug_mode and (self._import_error_callback is not None):
                self._import_error_callback(e)
            else:
                raise e

    def __try_import(self):
        if self._mod is None:
            self._mod = import_module(self._name)
            self._member_obj = getattr(self._mod, self._member)
