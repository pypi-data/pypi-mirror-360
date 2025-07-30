import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class List(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TList],
    ):
        super().__init__("a-list")

        self.props(handle_props(kwargs))  # type: ignore

    def on_scroll(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "scroll",
            handler,
            extends=extends,
        )
        return self

    def on_reach_bottom(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "reach-bottom",
            handler,
            extends=extends,
        )
        return self

    def on_page_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "page-change",
            handler,
            extends=extends,
        )
        return self

    def on_page_size_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "page-size-change",
            handler,
            extends=extends,
        )
        return self
