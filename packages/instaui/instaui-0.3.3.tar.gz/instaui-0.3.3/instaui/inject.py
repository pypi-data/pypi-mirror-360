import typing
from instaui.runtime import ui_state_scope


_T = typing.TypeVar("_T")


def injection_key(key: str) -> _T:
    """creates a key for injection

    Args:
        key (str): key to use for injection

    Examples:
    .. code-block:: python
        text_key :str = injection_key("text")

        # state model
        class Person(ui.StateModel):
            name:str

        person_key :Person = injection_key(Person(name='foo'))
    """
    return key  # type: ignore


def inject_state(key: _T) -> _T:
    return typing.cast(_T, ui_state_scope.load_state(key))  # type: ignore


def provide_state(key: _T, obj: _T) -> _T:
    ui_state_scope.save_state(key, obj)
    return obj
