from typing import Dict, Generic, TypeVar, Protocol
from abc import ABC, abstractmethod

T = TypeVar("T")


class ElementBindingMixin(ABC, Generic[T]):
    @abstractmethod
    def _to_element_binding_config(self) -> Dict:
        pass


class ElementBindingProtocol(Protocol):
    def _to_element_binding_config(self) -> Dict: ...
