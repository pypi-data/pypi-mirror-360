import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Avatar(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TAvatar],
    ):
        super().__init__("a-avatar")

        self.props(handle_props(kwargs))  # type: ignore

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "click",
            handler,
            extends=extends,
        )
        return self

    def on_error(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "error",
            handler,
            extends=extends,
        )
        return self

    def on_load(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "load",
            handler,
            extends=extends,
        )
        return self
