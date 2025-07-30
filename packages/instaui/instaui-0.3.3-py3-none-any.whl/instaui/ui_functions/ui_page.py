from typing import Callable
from instaui.launch_collector import get_launch_collector, PageInfo


def page(path: str = "/"):
    """Register a page route.

    Args:
        path (str): The route path.
    """

    def wrapper(func: Callable):
        get_launch_collector().register_page(PageInfo(path, func))
        return func

    return wrapper
