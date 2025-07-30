from __future__ import annotations
from typing import Dict, List
from instaui.common.jsonable import Jsonable
from instaui.components.component import Component
from instaui.runtime.scope import Scope

from . import _types
from ._route_model import RouteCollector


class RouterBox_(Jsonable):
    def __init__(self):
        self._mode: _types.TRouterHistoryMode = "web"
        self._keep_alive: bool = False
        self._component_map: Dict[str, Dict] = {}
        self._route_collector: RouteCollector = RouteCollector()

    def add_component(
        self,
        path: str,
        components: List[Component],
        scope: Scope,
        lazy_loading: bool = False,
    ):
        config = {"items": components, "scope": scope}
        if lazy_loading:
            config["lazy"] = True

        self._component_map[path] = config

    def _to_json_dict(self):
        data = {}

        data["routes"] = self._route_collector.model_dump(exclude_none=True)["routes"]
        data["mode"] = self._mode

        if self._keep_alive is not False:
            data["kAlive"] = self._keep_alive

        return data
