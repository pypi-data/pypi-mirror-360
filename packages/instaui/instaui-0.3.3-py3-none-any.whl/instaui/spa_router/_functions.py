import typing
from . import _types
from instaui.runtime._app import get_app_slot
from . import _install
from ._router_param_var import RouteParamsVar
from ._router_output import RouterOutput, RouterMethod
from ._route_model import RouteItem

_ASSERT_MSG = "Router is not initialized."


def add_route(
    page_fn: typing.Callable,
    *,
    name: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    children: typing.Optional[typing.List[RouteItem]] = None,
    lazy_loading: bool = False,
):
    _install.try_register_router_collector()
    route_collector = get_app_slot()._route_collector
    assert route_collector is not None, _ASSERT_MSG
    route_collector.add_route(
        RouteItem.create(
            path=path,
            component_fn=page_fn,
            name=name,
            children=children,
        )
    )


def config_router(
    routes: typing.Optional[typing.List[RouteItem]] = None,
    *,
    history: _types.TRouterHistoryMode = "hash",
    keep_alive: bool = False,
):
    """Configure the router.

    Examples:
    .. code-block:: python
        routes = [
            spa_router.RouteItem.create(path='/',component_fn=home),
            spa_router.RouteItem.create(path='/user',component_fn=user_home),
        ]

        spa_router.config_router(routes=routes)

    Args:
        routes (typing.Optional[typing.List[RouteItem]], optional): list of routes to be added to the router. Defaults to None.
        history (_types.TRouterHistoryMode, optional): router history mode. Can be "web", "memory" or "hash". Defaults to "hash".
        keep_alive (bool, optional): whether to keep the components alive when navigating to a new route.Defaults to False.
    """

    _install.try_register_router_collector()

    route_collector = get_app_slot()._route_collector
    assert route_collector is not None, _ASSERT_MSG

    route_collector.mode = history
    route_collector.keep_alive = keep_alive
    route_collector.routes = routes or []


def get_params(param_name: str) -> typing.Any:
    return RouteParamsVar("params")[param_name]


def get_path():
    return RouteParamsVar("path")


def get_full_path():
    return RouteParamsVar("fullPath")


def push(
    *,
    path: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    params: typing.Optional[typing.Dict[str, typing.Any]] = None,
    query: typing.Optional[typing.Dict[str, typing.Any]] = None,
    hash: typing.Optional[str] = None,
):
    method_params: typing.Dict = {}

    if path is not None:
        method_params["path"] = path
    if name is not None:
        method_params["name"] = name

    if params is not None:
        method_params["params"] = params
    if query is not None:
        method_params["query"] = query
    if hash is not None:
        method_params["hash"] = hash

    return RouterMethod(
        fn="push",
        args=[method_params],
    )


def go(n: int):
    return RouterMethod(
        fn="go",
        args=[n],
    )


def forward():
    return go(1)


def back():
    return go(-1)


def output():
    return RouterOutput()
