from __future__ import annotations
import datetime
import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Calendar(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[datetime.date]] = None,
        **kwargs: Unpack[component_types.TCalendar],
    ):
        super().__init__("a-calendar")

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

    def on_panel_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "panel-change",
            handler,
            extends=extends,
        )
        return self
