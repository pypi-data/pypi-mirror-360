from abc import ABC, abstractmethod
import typing


class EventMixin(ABC):
    @abstractmethod
    def copy_with_extends(self, extends: typing.Sequence) -> "EventMixin":
        pass

    @abstractmethod
    def event_type(self) -> typing.Literal["web", "js"]:
        pass
