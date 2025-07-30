import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Form(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TForm],
    ):
        super().__init__("a-form")

        self.props(handle_props(kwargs))  # type: ignore

    def on_submit(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "submit",
            handler,
            extends=extends,
        )
        return self

    def on_submit_success(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "submit-success",
            handler,
            extends=extends,
        )
        return self

    def on_submit_failed(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "submit-failed",
            handler,
            extends=extends,
        )
        return self
