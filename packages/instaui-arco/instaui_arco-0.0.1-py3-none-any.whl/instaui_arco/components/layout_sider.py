import typing
from typing_extensions import TypedDict, Unpack
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class TLayoutSider(TypedDict, total=False):
    theme: typing.Literal["dark", "light"]
    collapsed: bool
    default_collapsed: bool
    collapsible: bool
    width: int
    collapsed_width: int
    reverse_arrow: bool
    breakpoint: typing.Literal["xxl", "xl", "lg", "md", "sm", "xs"]
    resize_directions: typing.List[typing.Literal["left", "right", "top", "bottom"]]
    hide_trigger: bool


class LayoutSider(Element):
    def __init__(
        self,
        **kwargs: Unpack[TLayoutSider],
    ):
        super().__init__("a-layout-sider")
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

    def on_breakpoint(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "breakpoint",
            handler,
            extends=extends,
        )
        return self
