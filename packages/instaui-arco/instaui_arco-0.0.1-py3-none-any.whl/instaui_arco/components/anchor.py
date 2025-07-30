import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Anchor(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TAnchor],
    ):
        super().__init__("a-anchor")

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

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self
