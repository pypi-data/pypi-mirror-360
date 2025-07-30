from __future__ import annotations

import ast
from copy import copy
import inspect
from pathlib import Path
import re
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    ClassVar,
    Literal,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import Self
from collections import defaultdict
from instaui.runtime._app import get_app_slot
from instaui.vars.element_ref import ElementRef
from instaui.vars.vfor_item import VForItem
from instaui.components.directive import Directive
from instaui.dependencies.component_dependency import (
    ComponentDependencyInfo,
)
from .slot import SlotManager, Slot
from instaui import consts
from instaui.components.component import Component

from instaui.vars.mixin_types.element_binding import (
    ElementBindingMixin,
    ElementBindingProtocol,
)
from instaui.vars.mixin_types.observable import ObservableMixin

if TYPE_CHECKING:
    from instaui.event.event_mixin import EventMixin
    from instaui.vars.types import TMaybeRef


TVarGetterStrategy = Union[Literal["as_needed", "all"], List]

# Refer to the NiceGUI project.
# https://github.com/zauberzeug/nicegui/blob/main/nicegui/element.py
PROPS_PATTERN = re.compile(
    r"""
# Match a key-value pair optionally followed by whitespace or end of string
([:\w\-]+)          # Capture group 1: Key
(?:                 # Optional non-capturing group for value
    =               # Match the equal sign
    (?:             # Non-capturing group for value options
        (           # Capture group 2: Value enclosed in double quotes
            "       # Match  double quote
            [^"\\]* # Match any character except quotes or backslashes zero or more times
            (?:\\.[^"\\]*)*  # Match any escaped character followed by any character except quotes or backslashes zero or more times
            "       # Match the closing quote
        )
        |
        (           # Capture group 3: Value enclosed in single quotes
            '       # Match a single quote
            [^'\\]* # Match any character except quotes or backslashes zero or more times
            (?:\\.[^'\\]*)*  # Match any escaped character followed by any character except quotes or backslashes zero or more times
            '       # Match the closing quote
        )
        |           # Or
        ([\w\-.%:\/]+)  # Capture group 4: Value without quotes
    )
)?                  # End of optional non-capturing group for value
(?:$|\s)            # Match end of string or whitespace
""",
    re.VERBOSE,
)


class Element(Component):
    dependency: ClassVar[Optional[ComponentDependencyInfo]] = None
    _default_props: ClassVar[Dict[str, Any]] = {}
    _default_classes: ClassVar[List[str]] = []
    _default_style: ClassVar[Dict[str, str]] = {}

    def __init__(self, tag: Optional[Union[str, ElementBindingProtocol]] = None):
        if self.dependency:
            tag = self.dependency.tag_name or ""

        super().__init__(tag)

        self._str_classes: List[str] = []
        self._dict_classes: Dict[str, ElementBindingMixin[bool]] = {}
        self._bind_str_classes: List[ElementBindingMixin[str]] = []
        self._str_classes.extend(self._default_classes)
        self._style: Dict[str, str] = {}
        self._style.update(self._default_style)
        self._style_str_binds: List[ElementBindingMixin[str]] = []
        self._props: Dict[str, Any] = {}
        self._props.update(self._default_props)
        self._proxy_props: List[ElementBindingMixin] = []

        self._events: defaultdict[str, List[EventMixin]] = defaultdict(list)
        self._directives: Dict[Directive, None] = {}

        self._slot_manager = SlotManager()
        self.__element_ref: Optional[ElementRef] = None
        self.__var_getter_strategy: TVarGetterStrategy = "as_needed"

    def __init_subclass__(
        cls,
        *,
        esm: Union[str, Path, None] = None,
        externals: Optional[Dict[str, Path]] = None,
        css: Union[List[Union[str, Path]], None] = None,
    ) -> None:
        super().__init_subclass__()

        if esm:
            esm = _make_dependency_path(esm, cls)

            if externals:
                externals = {
                    key: _make_dependency_path(value, cls)
                    for key, value in externals.items()
                }

            if css:
                css = set(_make_dependency_path(c, cls) for c in css)  # type: ignore

            tag_name = f"instaui-{esm.stem}"

            cls.dependency = ComponentDependencyInfo(
                tag_name=tag_name,
                esm=esm,
                externals=cast(Dict[str, Path], externals or {}),
                css=cast(Set[Path], css or set()),
            )

        cls._default_props = copy(cls._default_props)
        cls._default_classes = copy(cls._default_classes)
        cls._default_style = copy(cls._default_style)

    def on_mounted(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        return self.on(
            ":mounted",
            handler=handler,
            extends=extends,
        )

    def _set_var_getter_strategy(self, strategy: TVarGetterStrategy):
        """Set the strategy for getting variables.

        # Example:
        .. code-block:: python
            self._set_var_getter_strategy("all")

            # or
            a = ui.state(1)
            b = ui.state(2)
            self._set_var_getter_strategy([a,b])

        """
        self.__var_getter_strategy = strategy

    def scoped_style(self, style: str, *, selector="*", with_self=False):
        app = get_app_slot()
        ssid = app.gen_scoped_style_group_id()

        select_box = f"*[insta-scoped-style={ssid}]"
        real_selector = f"{select_box} {selector}"

        if with_self:
            real_selector = f"{select_box},{real_selector}"

        real_selector = f":where({real_selector})"
        style_code = f"{real_selector} {{ {style} }}"

        self.props({"insta-scoped-style": ssid})
        app._html_resource.add_style_tag(
            style_code, group_id=consts.SCOPED_STYLE_GROUP_ID
        )
        return self

    def slot_props(self, name: str):
        return self._slot_manager.default.slot_props(name)

    @staticmethod
    def _update_classes(
        classes: List[str],
        add: str,
    ) -> List[str]:
        return list(dict.fromkeys(classes + add.split()))

    @staticmethod
    def _parse_style(text: Union[str, Dict[str, str]]) -> Dict[str, str]:
        if isinstance(text, dict):
            return text

        if not text:
            return {}

        result = {}
        for item in text.split(";"):
            item = item.strip()
            if item:
                key, value = item.split(":")
                key = key.strip()
                value = value.strip()
                result[key] = value

        return result

    @staticmethod
    def _parse_props(props: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(props, dict):
            return props

        if not props:
            return {}

        dictionary = {}
        for match in PROPS_PATTERN.finditer(props or ""):
            key = match.group(1)
            value = match.group(2) or match.group(3) or match.group(4)
            if value is None:
                dictionary[key] = True
            else:
                if (value.startswith("'") and value.endswith("'")) or (
                    value.startswith('"') and value.endswith('"')
                ):
                    value = ast.literal_eval(value)
                dictionary[key] = value
        return dictionary

    def key(self, key: Any):
        """Set the key prop of the component.

        Args:
            key (str): The key prop value.

        """
        self.props({"key": key})
        return self

    def vmodel(
        self,
        value: Any,
        modifiers: Union[consts.TModifier, List[consts.TModifier], None] = None,
        *,
        prop_name: str = "value",
        is_html_component=False,
    ):
        if prop_name == "value":
            prop_name = "modelValue"

        modifiers = modifiers or []
        if isinstance(modifiers, str):
            modifiers = [modifiers]

        self.directive(
            Directive(
                is_sys=is_html_component,
                name="vmodel",
                arg=prop_name,
                modifiers=modifiers,
                value=value,  # type: ignore
            )
        )

        if is_html_component is False:
            model_modifiers = {m: True for m in modifiers}
            self.props({"modelModifiers": model_modifiers})

        return self

    def add_slot(self, name: str) -> Slot:
        return self._slot_manager.get_slot(name)

    @overload
    def classes(self, add: str) -> Self: ...
    @overload
    def classes(self, add: Dict[str, TMaybeRef[bool]]) -> Self: ...

    @overload
    def classes(self, add: TMaybeRef[str]) -> Self: ...

    def classes(
        self,
        add: Union[
            str,
            Dict[str, TMaybeRef[bool]],
            TMaybeRef[str],
            VForItem,
        ],
    ) -> Self:
        """Add classes to the component.

        Args:
            add (Union[ str, Dict[str, TMaybeRef[bool]], TMaybeRef[str], VForItem, ]): classes to add.


        Examples:
        .. code-block:: python

            elemelt = html.span('test')
            elemelt.classes('class1 class2')

            # dynamically classes
            class_name = ui.state('x')
            elemelt.classes(class_name)

            # apply name if True
            apply = ui.state(True)
            elemelt.classes({'x': apply})
        """

        if isinstance(add, str):
            self._str_classes = self._update_classes(self._str_classes, add)

        if isinstance(add, dict):
            self._dict_classes.update(**add)  # type: ignore

        if isinstance(add, ElementBindingMixin):
            self._bind_str_classes.append(add)  # type: ignore

        return self

    def style(self, add: Union[str, Dict[str, Any], TMaybeRef[str]]) -> Self:
        if isinstance(add, dict):
            add = {key: value for key, value in add.items()}

        if isinstance(add, ElementBindingMixin):
            self._style_str_binds.append(add)
            return self

        new_style = self._parse_style(add)
        self._style.update(new_style)
        return self

    def props(self, add: Union[str, Dict[str, Any], TMaybeRef]) -> Self:
        if isinstance(add, ElementBindingMixin):
            self._proxy_props.append(add)
            return self

        if isinstance(add, dict):
            add = {key: value for key, value in add.items() if value is not None}

        new_props = self._parse_props(add)
        self._props.update(new_props)
        return self

    @classmethod
    def default_classes(cls, add: str) -> type[Self]:
        cls._default_classes = cls._update_classes(cls._default_classes, add)
        return cls

    @classmethod
    def default_style(cls, add: Union[str, Dict[str, str]]) -> type[Self]:
        new_style = cls._parse_style(add)
        cls._default_style.update(new_style)
        return cls

    @classmethod
    def default_props(cls, add: Union[str, Dict[str, Any]]) -> type[Self]:
        new_props = cls._parse_props(add)
        cls._default_props.update(new_props)
        return cls

    def on(
        self,
        event_name: str,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        if extends:
            handler = handler.copy_with_extends(extends)

        self._events[event_name].append(handler)

        return self

    def directive(self, directive: Directive) -> Self:
        self._directives[directive] = None
        return self

    def display(self, value: Union[ElementBindingProtocol, bool]) -> Self:
        return self.directive(Directive(is_sys=False, name="vshow", value=value))

    def event_dataset(self, data: Any, name: str = "event-data") -> Self:
        from instaui.vars.js_computed import JsComputed

        value = JsComputed(inputs=[data], code="(data)=> JSON.stringify(data)")
        self.props({f"data-{name}": value})
        return self

    def element_ref(self, ref: ElementRef):
        self.__element_ref = ref
        return self

    def update_dependencies(
        self,
        *,
        css: Optional[Iterable[Path]] = None,
        externals: Optional[Dict[str, Path]] = None,
        replace: bool = False,
    ):
        if not self.dependency:
            return

        app = get_app_slot()
        dep = self.dependency.copy()
        if replace:
            dep.css.clear()
            dep.externals.clear()

        if css:
            dep.css.update(css)

        if externals:
            dep.externals.update(externals)

        app.add_temp_component_dependency(dep)

    def use(self, *use_fns: Callable[[Self], None]) -> Self:
        """Use functions to the component object.

        Args:
            use_fns (Callable[[Self], None]): The list of use functions.

        Examples:
        .. code-block:: python
            def use_red_color(element: html.paragraph):
                element.style('color: red')

            html.paragraph('Hello').use(use_red_color)
        """

        for fn in use_fns:
            fn(self)
        return self

    @classmethod
    def use_init(cls, init_fn: Callable[[type[Self]], Self]) -> Self:
        """Use this method to initialize the component.

        Args:
            init_fn (Callable[[type[Self]], Self]): The initialization function.

        Examples:
        .. code-block:: python
            def fack_init(cls: type[html.table]) -> html.table:
                return cls(columns=['name', 'age'],rows = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}])

            ui.table.use_init(fack_init)
        """
        return init_fn(cls)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._style or self._style_str_binds:
            value_styles, bind_styles = _classifyBindableDict(self._style)
            if value_styles:
                data["style"] = value_styles

            b_style_list = []

            if bind_styles:
                b_style_list.append(bind_styles)

            if self._style_str_binds:
                b_style_list.append(
                    [v._to_element_binding_config() for v in self._style_str_binds]
                )

            if b_style_list:
                data["bStyle"] = b_style_list

        if self._str_classes or self._dict_classes or self._bind_str_classes:
            data["classes"] = _normalize_classes_data(
                self._str_classes, self._dict_classes, self._bind_str_classes
            )

        if self._props:
            value_props, bind_props = _classifyBindableDict(self._props)

            if value_props:
                data["props"] = value_props

            if bind_props:
                data["bProps"] = bind_props

        if self._proxy_props:
            data["proxyProps"] = [
                v._to_element_binding_config() for v in self._proxy_props
            ]

        if self._events:
            data["events"] = _normalize_events(self._events)

        if self._slot_manager.has_slot():
            data["slots"] = self._slot_manager

        if self._directives:
            data["dir"] = list(self._directives.keys())

        if self.dependency:
            app_slot = get_app_slot()
            tag_name = self.dependency.tag_name
            app_slot.use_component_dependency(
                app_slot.get_temp_component_dependency(tag_name, self.dependency)
            )

        if self.__element_ref:
            data["eRef"] = self.__element_ref._to_element_binding_config()

        if self.__var_getter_strategy != "as_needed":
            data["varGetterStrategy"] = (
                [
                    cast(ObservableMixin, v)._to_observable_config()
                    for v in self.__var_getter_strategy
                ]
                if isinstance(self.__var_getter_strategy, list)
                else self.__var_getter_strategy
            )

        return data


def _normalize_events(
    events: defaultdict[str, List[EventMixin]],
):
    return {
        _normalize_event_name(name): event_list for name, event_list in events.items()
    }


def _normalize_event_name(event_name: str):
    """'click' -> 'onClick' , 'press-enter' -> 'onPressEnter' , 'pressEnter' -> 'onPressEnter'"""

    if event_name.startswith("on-"):
        event_name = event_name[3:]

    if event_name.startswith("on"):
        event_name = event_name[2:]

    parts = event_name.split("-")
    formatted_parts = [part[0].upper() + part[1:] for part in parts]

    return "".join(["on", *formatted_parts])


def _normalize_classes_data(
    str_classes: List[str],
    dict_classes: Dict[str, ElementBindingMixin[bool]],
    bind_str_classes: List[ElementBindingMixin[str]],
):
    _str_result = " ".join(str_classes)

    _dict_classes = {k: v._to_element_binding_config() for k, v in dict_classes.items()}

    _bind_str_classes = [v._to_element_binding_config() for v in bind_str_classes]

    if _dict_classes or _bind_str_classes:
        result = {}

        if _str_result:
            result["str"] = _str_result

        if _dict_classes:
            result["map"] = _dict_classes

        if _bind_str_classes:
            result["bind"] = _bind_str_classes

        return result
    else:
        return _str_result


def _classifyBindableDict(
    data: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return value_data, bind_data

    Args:
        data (Dict[str, Any]): _description_

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: _description_
    """

    value_data = {}
    bind_data = {}

    for key, value in data.items():
        if isinstance(value, ElementBindingMixin):
            bind_data[key] = value._to_element_binding_config()
        else:
            value_data[key] = value

    return value_data, bind_data


def _make_dependency_path(path: Union[str, Path], cls: type):
    if isinstance(path, str):
        path = Path(path)

    if not path.is_absolute():
        path = Path(inspect.getfile(cls)).parent / path

    return path
