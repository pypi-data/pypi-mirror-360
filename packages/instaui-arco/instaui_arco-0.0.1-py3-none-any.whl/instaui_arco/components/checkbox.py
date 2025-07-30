import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Checkbox(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[typing.Union[str, int, bool]]] = None,
        **kwargs: Unpack[component_types.TCheckbox],
    ):
        super().__init__("a-checkbox")

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
