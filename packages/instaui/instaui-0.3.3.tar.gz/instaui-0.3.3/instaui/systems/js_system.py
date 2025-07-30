import json


def py_value_to_js(value):
    if isinstance(value, str):
        return f"`{value}`"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    elif isinstance(value, dict):
        items = ", ".join(
            f"{json.dumps(k)}: {py_value_to_js(v)}" for k, v in value.items()
        )
        return f"{{{items}}}"
    elif isinstance(value, list):
        items = ", ".join(py_value_to_js(v) for v in value)
        return f"[{items}]"
    else:
        raise TypeError(f"Unsupported type: {type(value)}")
