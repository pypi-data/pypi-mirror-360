from __future__ import annotations
from typing import List, Optional
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.event.event_mixin import EventMixin


class Timer(Element, esm="./timer.js"):
    """
    A timer component that triggers events at specified intervals.

    Args:
        interval_seconds (float): Time in seconds between repeated events.
        active (Optional[TMaybeRef[bool]], optional): If True, starts the timer immediately.
            Accepts reactive values (e.g., state references) for dynamic control. Defaults to None (equivalent to True).
        immediate (Optional[bool], optional): If True, triggers the first event immediately. Defaults to None (equivalent to True).

    Example:
    .. code-block:: python
        from instaui import ui, html

        @ui.page('/')
        def index():
            x = ui.state(0)
            active = ui.state(True)

            @ui.event(inputs=[x], outputs=[x])
            def on_tick(x):
                return x + 1

            ui.timer(1, active=active).on_tick(on_tick)

            html.checkbox(active)
            html.span(x)
    """

    def __init__(
        self,
        interval_seconds: float,
        *,
        active: Optional[TMaybeRef[bool]] = None,
        immediate: Optional[bool] = None,
    ):
        super().__init__("template")

        self.props(
            {
                "intervalSeconds": interval_seconds,
                "active": active,
                "immediate": immediate,
            }
        )

    def on_tick(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        """
        Registers an event handler for the "tick" event.
        """
        return self.on("tick", handler, extends=extends)

    def on_stop(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        """
        Registers an event handler for the "stop" event.
        """

        return self.on("stop", handler, extends=extends)

    @classmethod
    def once(cls, delay_seconds: float):
        """
        Creates a timer that triggers only once.

        Args:
            delay_seconds (float): Time in seconds before the timer triggers.

        Example:
        .. code-block:: python
            msg = ui.state('')
            on_done = ui.js_event(outputs=[msg],code="()=> 'Done!'")

            ui.timer.once(1).on_tick(on_done)
            html.span(msg) # will show "Done!" after 1 second

        """
        return cls(delay_seconds, immediate=False).props({"once": True})
