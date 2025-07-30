import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Modal(Element):
    def __init__(
        self,
        visible_value: typing.Optional[TMaybeRef[bool]] = None,
        **kwargs: Unpack[component_types.TModal],
    ):
        super().__init__("a-modal")

        try_setup_vmodel(self, visible_value, prop_name="visible")
        self.props(handle_props(kwargs))  # type: ignore

    def on_ok(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "ok",
            handler,
            extends=extends,
        )
        return self

    def on_cancel(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cancel",
            handler,
            extends=extends,
        )
        return self

    def on_open(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "open",
            handler,
            extends=extends,
        )
        return self

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

    def on_before_open(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "before-open",
            handler,
            extends=extends,
        )
        return self

    def on_before_close(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "before-close",
            handler,
            extends=extends,
        )
        return self
