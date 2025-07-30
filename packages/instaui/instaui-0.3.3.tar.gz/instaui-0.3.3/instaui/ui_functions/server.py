from typing import Union
from instaui.runtime.context import get_context


def create_server(
    debug: bool = False,
    use_gzip: Union[int, bool] = True,
):
    """
    Create a new server instance.

    Note: When deploy to production, you need to set `debug=False`

    Args:
        debug (bool): Whether to run in debug mode. In debug mode, it has the development hot-reload feature. Defaults to False.
        use_gzip (Union[int, bool], optional):  Whether to use gzip compression. If an integer is provided, it will be used as the minimum response size for compression. If True, the default minimum size of 500 bytes will be used. If False, compression will not be used. Defaults to True.
    """
    from instaui.fastapi_server.server import Server

    context = get_context()
    context._app_mode = "web"
    context._debug_mode = debug

    return Server(use_gzip=use_gzip)
