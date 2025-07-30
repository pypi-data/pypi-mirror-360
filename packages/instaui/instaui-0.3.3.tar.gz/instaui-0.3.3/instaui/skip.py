from typing import Any


class _Skip:
    pass


skip_output = _Skip()


def is_skip_output(value: Any):
    return value is skip_output
