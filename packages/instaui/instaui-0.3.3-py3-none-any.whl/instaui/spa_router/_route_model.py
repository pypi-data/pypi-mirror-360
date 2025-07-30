from __future__ import annotations
import typing
from pydantic import BaseModel, Field, ConfigDict, field_serializer, model_serializer

from instaui.components.html.div import Div
from instaui.runtime._app import get_app_slot, get_current_scope
from instaui.components.component import Component
from instaui.common.jsonable import dumps2dict

from . import _types


class RouteItem(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    component_fn: typing.Optional[typing.Callable] = Field(exclude=True)
    sid: typing.Optional[str] = None
    vue_route_item: VueRouteItem = Field(serialization_alias="vueItem")
    meta: typing.Optional[typing.Dict] = None

    @model_serializer
    def model_ser(self):
        if self.component_fn is None and (not self.vue_route_item.path):
            raise ValueError("Either component_fn or vue_route_item.path must be set")

        if self.component_fn is None:
            return {
                "vueItem": self.vue_route_item,
            }

        if self.vue_route_item.path is None:
            self.vue_route_item.path = f"/{'' if self.component_fn.__name__ == 'index' else self.component_fn.__name__}"

        app = get_app_slot()
        with Div() as div:
            self.component_fn()
            scope_id = get_current_scope().id

        app.items.pop()

        self.vue_route_item.component = div._slot_manager.default._children

        return {
            "sid": scope_id,
            "vueItem": self.vue_route_item,
        }

    @classmethod
    def create(
        cls,
        *,
        component_fn: typing.Optional[typing.Callable] = None,
        path: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        params: typing.Optional[typing.Dict[str, str]] = None,
        children: typing.Optional[typing.List[RouteItem]] = None,
        meta: typing.Optional[typing.Dict] = None,
    ):
        """Create a new RouteItem

        Examples:
        .. code-block:: python
            routes = [
                spa_router.RouteItem.create(path='/',component_fn=home),
                spa_router.RouteItem.create(path='/user',component_fn=user_home),
            ]

            spa_router.config_router(routes=routes)

        Args:
            component_fn (typing.Callable): function that returns a component to be rendered.
            path (typing.Optional[str], optional): route path. Defaults to None.
            name (typing.Optional[str], optional): route name. Defaults to None.
            params (typing.Optional[typing.Dict[str, str]], optional): route params. Defaults to None.
            children (typing.Optional[typing.List[RouteItem]], optional): child routes. Defaults to None.

        """

        return cls(
            component_fn=component_fn,
            meta=meta,
            vue_route_item=VueRouteItem(
                path=path,
                name=name,
                params=params,
                component=[],
                children=children,
            ),
        )


class VueRouteItem(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: typing.Optional[str] = None
    params: typing.Optional[typing.Dict[str, str]] = None
    name: typing.Optional[str] = None
    component: typing.Optional[typing.List[Component]] = []
    children: typing.Optional[typing.List[RouteItem]] = None

    @field_serializer("component")
    def serialize_component(self, value: typing.List[Component]):
        if not value:
            return []
        return dumps2dict(value)


class RouteCollector(BaseModel):
    mode: _types.TRouterHistoryMode = "hash"
    keep_alive: bool = Field(default=False, serialization_alias="kAlive")
    routes: typing.List[RouteItem] = []

    def add_route(self, item: RouteItem):
        self.routes.append(item)
        return self
