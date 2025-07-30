import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Tree(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TTree],
    ):
        super().__init__("a-tree")

        self.props(handle_props(kwargs))  # type: ignore

    def on_select(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "select",
            handler,
            extends=extends,
        )
        return self

    def on_check(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "check",
            handler,
            extends=extends,
        )
        return self

    def on_expand(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "expand",
            handler,
            extends=extends,
        )
        return self

    def on_drag_start(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "drag-start",
            handler,
            extends=extends,
        )
        return self

    def on_drag_end(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "drag-end",
            handler,
            extends=extends,
        )
        return self

    def on_drag_over(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "drag-over",
            handler,
            extends=extends,
        )
        return self

    def on_drag_leave(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "drag-leave",
            handler,
            extends=extends,
        )
        return self

    def on_drop(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "drop",
            handler,
            extends=extends,
        )
        return self
