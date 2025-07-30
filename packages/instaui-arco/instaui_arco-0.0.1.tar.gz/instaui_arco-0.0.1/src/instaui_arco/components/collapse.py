import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Collapse(Element):
    def __init__(
        self,
        active_key_value: typing.Optional[typing.List[typing.Union[str, int]]] = None,
        **kwargs: Unpack[component_types.TCollapse],
    ):
        super().__init__("a-collapse")

        try_setup_vmodel(self, active_key_value, prop_name="active-key")
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
