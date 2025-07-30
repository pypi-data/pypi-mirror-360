from typing import Callable
from instaui.launch_collector import get_launch_collector


def on_page_request_lifespan(fn: Callable):
    """Register a function to be called on each page request.

    Args:
        fn (Callable): A function to be called on each page request.

    Examples:
    .. code-block:: python
        @ui.on_page_request_lifespan
        def _():
            print("page request start")
            yield
            print("page request end")

        # can stop the lifespan by calling the returned function
        stop_lifespan = ui.on_page_request_lifespan(lambda: None)
        stop_lifespan()
    """

    remove_key = get_launch_collector().add_page_request_lifespan(fn)
    return lambda: get_launch_collector().remove_page_request_lifespan(remove_key)
