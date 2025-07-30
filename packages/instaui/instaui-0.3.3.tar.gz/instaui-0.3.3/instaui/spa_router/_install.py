from instaui.runtime._app import get_app_slot
from instaui.spa_router._route_model import RouteCollector


def try_register_router_collector():
    app = get_app_slot()
    if app._route_collector is not None:
        return

    rb = RouteCollector()
    app.register_router(rb)
