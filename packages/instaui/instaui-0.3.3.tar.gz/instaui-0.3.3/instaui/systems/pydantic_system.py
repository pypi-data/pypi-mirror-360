from typing import Protocol

import pydantic
import inspect


class TypeAdapterProtocol(Protocol):
    def to_python_value(self, value, *args, **kwargs): ...


class PydanticTypeAdapter:
    def __init__(self, type: type) -> None:
        self.type_adapter = pydantic.TypeAdapter(type)

    def to_python_value(self, value, *args, **kwargs):
        return self.type_adapter.validate_python(value)


class EmptyTypeAdapter:
    def to_python_value(self, value, *args, **kwargs):
        return value


def create_type_adapter(type: type) -> TypeAdapterProtocol:
    if type is inspect._empty:
        return EmptyTypeAdapter()
    return PydanticTypeAdapter(type)
