from abc import ABC, abstractmethod


class ObservableMixin(ABC):
    @abstractmethod
    def _to_observable_config(self):
        pass
