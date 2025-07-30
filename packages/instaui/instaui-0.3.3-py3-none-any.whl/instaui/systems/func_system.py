import inspect
from pathlib import Path
from typing import Any, Callable, Generator, List, Tuple, get_type_hints


def has_positional_or_keyword_arg(fn: Callable):
    signature = inspect.signature(fn)
    has_pos = False
    has_kw = False

    for param in signature.parameters.values():
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            has_pos = True
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            has_kw = True

    return has_pos, has_kw


def get_fn_params_infos(fn: Callable) -> List[Tuple[str, type]]:
    """Get the parameter names and types of a function

    Args:
        fn (function): _description_

    Returns:
        [('a', int), ('b', str)]
    """
    signature = inspect.signature(fn)
    type_hints = get_type_hints(fn)

    return [
        (name, type_hints.get(name, inspect._empty))
        for name in signature.parameters.keys()
    ]


def is_last_param_args(fn):
    """
    Returns:
        bool: True if the last parameter of the function is `*args`, False otherwise.
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())

    if not params:
        return False

    last_param = params[-1]
    return last_param.kind == inspect.Parameter.VAR_POSITIONAL


def get_required_param_count(fn: Callable):
    signature = inspect.signature(fn)
    params = signature.parameters

    return sum(
        1
        for param in params.values()
        if param.default is inspect.Parameter.empty
        and param.kind
        in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.KEYWORD_ONLY,
        )
    )


def get_function_param_names(fn):
    signature = inspect.signature(fn)
    return list(signature.parameters.keys())


def get_function_location_info(func) -> Tuple[str, int, str]:
    """

    Returns:
        Tuple[str, int, str]: A tuple containing the file path, start line number, and function name.
    """
    file_path = inspect.getfile(func)
    _, start_line = inspect.getsourcelines(func)

    return str(Path(file_path).resolve()), start_line, func.__qualname__


def iter_closures(fn: Callable):
    if not (hasattr(fn, "__closure__") and fn.__closure__):
        return

    stack = [fn]
    while stack:
        fn = stack.pop()

        if hasattr(fn, "__closure__") and fn.__closure__:
            for i, cell in enumerate(fn.__closure__, 1):
                try:
                    var_value = cell.cell_contents
                    var_name = fn.__code__.co_freevars[i - 1]
                    yield var_name, var_value

                    if callable(var_value):
                        stack.append(var_value)
                except ValueError:
                    continue


def make_fn_to_generator(
    fn,
) -> Callable[..., Generator[None, Any, None]]:
    if inspect.isgeneratorfunction(fn):
        return fn
    else:

        def wrapper(*args, **kwargs):
            fn(*args, **kwargs)
            yield

        return wrapper
