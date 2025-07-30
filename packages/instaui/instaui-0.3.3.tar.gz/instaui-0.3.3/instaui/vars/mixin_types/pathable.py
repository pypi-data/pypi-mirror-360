from typing import Dict
from abc import ABC, abstractmethod


class PathableMixin(ABC):
    @abstractmethod
    def _to_pathable_binding_config(self) -> Dict:
        pass


class CanPathPropMixin(ABC):
    @abstractmethod
    def _to_path_prop_binding_config(self) -> Dict:
        pass
