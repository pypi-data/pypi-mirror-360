import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class AutoComplete(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TAutocomplete],
    ):
        super().__init__("a-auto-complete")
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

    def on_search(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "search",
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

    def on_dropdown_scroll(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "dropdown-scroll",
            handler,
            extends=extends,
        )
        return self

    def on_dropdown_reach_bottom(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "dropdown-reach-bottom",
            handler,
            extends=extends,
        )
        return self
