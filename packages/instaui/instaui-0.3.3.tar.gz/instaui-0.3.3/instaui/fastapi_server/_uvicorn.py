from __future__ import annotations
from types import FrameType
import typing
import uvicorn
import socket


ThandleExitCallbacks = typing.List[typing.Callable[[], typing.Any]]


class UvicornServer(uvicorn.Server):
    instance: UvicornServer

    def __init__(self, config: uvicorn.Config) -> None:
        super().__init__(config)
        self._handle_exit_callbacks: ThandleExitCallbacks = []

    @classmethod
    def create_singleton(
        cls, config: uvicorn.Config, handle_exit_callbacks: ThandleExitCallbacks
    ) -> None:
        cls.instance = cls(config=config)
        for callback in handle_exit_callbacks:
            cls.instance.on_handle_exit(callback)

    def run(self, sockets: typing.Optional[typing.List[socket.socket]] = None) -> None:
        self.instance = self

        super().run()

    def on_handle_exit(self, callback: typing.Callable[[], typing.Any]):
        self._handle_exit_callbacks.append(callback)

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        for callback in self._handle_exit_callbacks:
            callback()
        return super().handle_exit(sig, frame)
