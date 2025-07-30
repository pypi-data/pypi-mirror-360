import asyncio
import logging
import typing
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from instaui.runtime.context import get_context
import uuid

DEBUG_SSE_URL = "/instaui/debug-sse"
logger = logging.getLogger(__name__)

_task_events: typing.Dict[str, asyncio.Event] = {}


def create_router(app: FastAPI):
    if get_context().debug_mode:
        _create_sse(app)


async def event_generator(
    request: Request, connection_id: str, interval_heart_beat_sec: float = 0.8
):
    logger.debug("debug sse started")
    task_event = asyncio.Event()
    _task_events[connection_id] = task_event

    try:
        while not task_event.is_set():
            if await request.is_disconnected():
                break

            yield "data:1\n\n"
            await asyncio.sleep(interval_heart_beat_sec)

    except asyncio.CancelledError:
        pass
    finally:
        if connection_id in _task_events:
            del _task_events[connection_id]


def _get_connection_id(request: Request):
    return str(uuid.uuid4())


def _create_sse(app: FastAPI):
    @app.get(DEBUG_SSE_URL)
    async def events(
        request: Request, connection_id: str = Depends(_get_connection_id)
    ):
        return StreamingResponse(
            event_generator(request, connection_id), media_type="text/event-stream"
        )


def when_server_reload():
    for task_id, task in _task_events.items():
        task.set()

    _task_events.clear()
