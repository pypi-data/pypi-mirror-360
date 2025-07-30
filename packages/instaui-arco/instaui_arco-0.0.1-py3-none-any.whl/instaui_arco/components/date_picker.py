import typing
from typing_extensions import Unpack
import datetime
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class DatePicker(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[datetime.datetime]] = None,
        **kwargs: Unpack[component_types.TDatepicker],
    ):
        super().__init__("a-date-picker")

        try_setup_vmodel(self, value)
        self.props(handle_props(kwargs))  # type: ignore

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

    def on_clear(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "clear",
            handler,
            extends=extends,
        )
        return self

    def on_select_shortcut(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "select-shortcut",
            handler,
            extends=extends,
        )
        return self

    def on_picker_value_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "picker-value-change",
            handler,
            extends=extends,
        )
        return self
