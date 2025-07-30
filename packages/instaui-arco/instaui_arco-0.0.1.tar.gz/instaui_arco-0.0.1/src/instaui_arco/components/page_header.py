import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class PageHeader(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TPageheader],
    ):
        super().__init__("a-page-header")

        self.props(handle_props(kwargs))  # type: ignore

    def on_back(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "back",
            handler,
            extends=extends,
        )
        return self
