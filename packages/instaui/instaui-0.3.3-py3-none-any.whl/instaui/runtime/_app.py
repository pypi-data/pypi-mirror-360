from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Set
from typing_extensions import Unpack, TypedDict
from instaui.common.jsonable import Jsonable
from .resource import HtmlResource
from instaui.consts import _T_App_Mode
from contextvars import ContextVar, Token
from instaui.runtime.scope import Scope, GlobalScope
from types import MappingProxyType

if TYPE_CHECKING:
    from instaui.components.component import Component
    from instaui.components.slot import Slot

    from instaui.dependencies.component_dependency import ComponentDependencyInfo
    from instaui.dependencies.plugin_dependency import PluginDependencyInfo
    from instaui.spa_router._route_model import RouteCollector


class App(Jsonable):
    _default_app_slot: ClassVar[Optional[App]] = None
    _web_server_info: ClassVar[Optional[Dict]] = None

    def __init__(self, *, mode: _T_App_Mode, meta: Optional[Dict] = None) -> None:
        super().__init__()
        self._scope_id_counter = 0
        self._scoped_style_id_counter = 0
        self._mode: _T_App_Mode = mode
        self.items: List[Component] = []
        self.meta = meta
        self._slots_stacks: List[Slot] = []

        defalut_scope = self.create_scope()
        self._scope_stack: List[Scope] = [defalut_scope]
        self._scopes: List[Scope] = [defalut_scope]
        self._sid = defalut_scope.id
        self._html_resource = HtmlResource()
        self._component_dependencies: Set[ComponentDependencyInfo] = set()
        self._temp_component_dependencies: Dict[str, ComponentDependencyInfo] = {}
        self._plugin_dependencies: Set[PluginDependencyInfo] = set()

        self._page_path: Optional[str] = None
        self._page_params: Dict[str, Any] = {}
        self._query_params: Dict[str, Any] = {}
        self._route_collector: Optional[RouteCollector] = None

    @property
    def mode(self) -> _T_App_Mode:
        return self._mode

    @property
    def top_scope(self) -> Scope:
        return self._scope_stack[0]

    @property
    def page_path(self) -> str:
        assert self._page_path is not None, "Page path is not set"
        return self._page_path  # type: ignore

    @property
    def page_params(self):
        return MappingProxyType(self._page_params)

    @property
    def query_params(self):
        return MappingProxyType(self._query_params)

    def create_scope(self) -> Scope:
        self._scope_id_counter += 1
        scope = Scope(str(self._scope_id_counter))
        return scope

    def gen_scoped_style_group_id(self):
        gid = f"scoped-style-{self._scoped_style_id_counter}"
        self._scoped_style_id_counter += 1
        return gid

    def reset_html_resource(self):
        self._html_resource = HtmlResource()

    def add_temp_component_dependency(self, dependency: ComponentDependencyInfo):
        self._temp_component_dependencies[dependency.tag_name] = dependency

    def get_temp_component_dependency(
        self, tag_name: str, default: ComponentDependencyInfo
    ) -> ComponentDependencyInfo:
        return self._temp_component_dependencies.get(tag_name, default)

    def has_temp_component_dependency(self, tag_name: str):
        return tag_name in self._temp_component_dependencies

    def use_component_dependency(
        self, dependency: ComponentDependencyInfo, *, replace=False
    ) -> None:
        if replace:
            self._component_dependencies.discard(dependency)

        self._component_dependencies.add(dependency)

    def use_plugin_dependency(self, dependency: PluginDependencyInfo) -> None:
        self._plugin_dependencies.add(dependency)

    def register_router(self, collector: RouteCollector) -> None:
        self._route_collector = collector

    def append_component_to_container(self, component: Component):
        if self._slots_stacks:
            self._slots_stacks[-1]._children.append(component)
        else:
            self.items.append(component)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._page_path:
            url_info = {"path": self.page_path}
            if self._page_params:
                url_info["params"] = self._page_params  # type: ignore

            data["url"] = url_info

        # data["scopes"] = self._scopes

        if self._route_collector is not None:
            data["router"] = self._route_collector.model_dump(
                exclude_defaults=True, by_alias=True
            )

        if self._web_server_info is not None:
            data["webInfo"] = self._web_server_info

        data["sid"] = self._sid

        return data

    @classmethod
    def _create_default(cls):
        if cls._default_app_slot is None:
            cls._default_app_slot = DefaultApp(mode="web")
        return cls._default_app_slot


class DefaultApp(App):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultApp, cls).__new__(cls)
        return cls._instance

    def create_scope(self) -> Scope:
        self._scope_id_counter += 1
        scope = GlobalScope(str(self._scope_id_counter))
        return scope

    def append_component_to_container(self, component: Component):
        raise ValueError("Operations are not allowed outside of ui.page")


_app_var: ContextVar[App] = ContextVar("_app_var", default=App._create_default())


def use_default_app_slot():
    assert App._default_app_slot is not None, "Default app slot is not set"
    _app_var.set(App._default_app_slot)


def get_default_app_slot():
    return App._create_default()


def get_app_slot() -> App:
    return _app_var.get()


def get_current_scope():
    current_scope = get_app_slot()._scope_stack[-1]
    if current_scope is None:
        raise ValueError("No current scope")
    return current_scope


class ready_scope:
    def __init__(self) -> None:
        self._scope = None

    @property
    def used(self) -> bool:
        return self._scope is not None

    @property
    def has_vars(self) -> bool:
        return self._scope.has_var  # type: ignore

    @property
    def scope(self) -> Scope:
        return self._scope  # type: ignore

    @property
    def scope_id(self) -> str:
        return self._scope.id  # type: ignore

    def __enter__(self):
        return self.enter()

    def __exit__(self, *_) -> None:
        self.exit(*_)

    def enter(self):
        if self._scope is not None:
            raise ValueError("Scope is already used")

        app = get_app_slot()
        self._scope = app.create_scope()
        app._scopes.append(self._scope)
        app._scope_stack.append(self._scope)

        return self._scope

    def exit(self, *_) -> None:
        get_app_slot()._scope_stack.pop()


def get_slot_stacks():
    return get_app_slot()._slots_stacks


def pop_slot():
    get_slot_stacks().pop()


def new_app_slot(mode: _T_App_Mode, app_meta: Optional[Dict] = None):
    return _app_var.set(App(mode=mode, meta=app_meta))


def reset_app_slot(token: Token[App]):
    _app_var.reset(token)


def in_default_app_slot():
    return isinstance(get_app_slot(), DefaultApp)


def check_default_app_slot_or_error(
    error_message="Operations are not allowed outside of ui.page",
):
    if isinstance(get_app_slot(), DefaultApp):
        raise ValueError(error_message)


class TWebServerInfo(TypedDict, total=False):
    watch_url: Optional[str]
    watch_async_url: Optional[str]
    event_url: Optional[str]
    event_async_url: Optional[str]


def update_web_server_info(**kwargs: Unpack[TWebServerInfo]):
    if App._web_server_info is None:
        App._web_server_info = {}

    data = {k: v for k, v in kwargs.items() if v is not None}

    App._web_server_info.update(data)
