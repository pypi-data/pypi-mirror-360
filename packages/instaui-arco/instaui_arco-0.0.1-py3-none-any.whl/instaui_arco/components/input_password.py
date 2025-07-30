import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from .input import Input
from ._utils import try_setup_vmodel


class TInputPassword(component_types.TInput, total=False):
    model_visibility: bool
    default_visibility: bool
    invisible_button: bool


class InputPassword(Input, exten_name="password"):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[str]] = None,
        *,
        visibility_value: typing.Optional[TMaybeRef[bool]] = None,
        **kwargs: Unpack[TInputPassword],
    ):
        super().__init__(value=value, **kwargs)
        try_setup_vmodel(self, visibility_value, prop_name="visibility")

    def on_visibility_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "visibility-change",
            handler,
            extends=extends,
        )
        return self
