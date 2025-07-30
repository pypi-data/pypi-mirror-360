import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Steps(Element):
    def __init__(
        self,
        current_value: typing.Optional[TMaybeRef[int]] = None,
        **kwargs: Unpack[component_types.TSteps],
    ):
        super().__init__("a-steps")

        try_setup_vmodel(self, current_value, prop_name="current")
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
