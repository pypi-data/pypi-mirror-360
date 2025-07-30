import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class PopConfirm(Element):
    def __init__(
        self,
        popup_visible_value: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TPopconfirm],
    ):
        super().__init__("a-popconfirm")

        try_setup_vmodel(self, popup_visible_value, prop_name="popup-visible")
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
