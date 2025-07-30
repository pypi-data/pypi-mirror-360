import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Tooltip(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TTooltip],
    ):
        super().__init__("a-tooltip")

        self.props(handle_props(kwargs))  # type: ignore

    def on_popup_visible_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "popup-visible-change",
            handler,
            extends=extends,
        )
        return self
