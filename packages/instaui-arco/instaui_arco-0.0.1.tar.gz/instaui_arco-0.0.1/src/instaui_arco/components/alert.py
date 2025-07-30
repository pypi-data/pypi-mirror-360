import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Alert(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TAlert],
    ):
        super().__init__("a-alert")

        self.props(handle_props(kwargs))  # type: ignore

    def on_close(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "close",
            handler,
            extends=extends,
        )
        return self

    def on_after_close(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "after-close",
            handler,
            extends=extends,
        )
        return self
