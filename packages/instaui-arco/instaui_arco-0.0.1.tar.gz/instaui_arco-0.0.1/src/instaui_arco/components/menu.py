import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.components.content import Content
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Menu(Element):
    def __init__(
        self,
        collapsed_value: typing.Optional[TMaybeRef[bool]] = None,
        **kwargs: Unpack[component_types.TMenu],
    ):
        super().__init__("a-menu")

        try_setup_vmodel(self, collapsed_value, prop_name="collapsed")
        self.props(handle_props(kwargs))  # type: ignore

    def on_collapse(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "collapse",
            handler,
            extends=extends,
        )
        return self

    def on_menu_item_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "menu-item-click",
            handler,
            extends=extends,
        )
        return self

    def on_sub_menu_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "sub-menu-click",
            handler,
            extends=extends,
        )
        return self


class MenuItem(Element):
    def __init__(self, title: typing.Optional[TMaybeRef[str]] = None):
        super().__init__("a-menu-item")

        if title is not None:
            with self:
                Content(title)

    def icon_slot(self):
        return self.add_slot("icon")


class SubMenu(Element):
    def __init__(
        self,
        title: typing.Optional[TMaybeRef[str]] = None,
    ):
        super().__init__("a-sub-menu")
        if title is not None:
            with self.title_slot():
                Content(title)

    def icon_slot(self):
        return self.add_slot("icon")

    def title_slot(self):
        return self.add_slot("title")
