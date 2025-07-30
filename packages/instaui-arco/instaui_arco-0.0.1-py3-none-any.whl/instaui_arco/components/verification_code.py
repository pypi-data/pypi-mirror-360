import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class VerificationCode(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TVerificationcode],
    ):
        super().__init__("a-verification-code")

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

    def on_finish(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "finish",
            handler,
            extends=extends,
        )
        return self

    def on_input(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "input",
            handler,
            extends=extends,
        )
        return self
