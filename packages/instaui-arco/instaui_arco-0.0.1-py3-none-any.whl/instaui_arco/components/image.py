import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Image(Element):
    def __init__(
        self,
        *,
        preview_visible_value: typing.Optional[TMaybeRef[bool]] = None,
        **kwargs: Unpack[component_types.TImage],
    ):
        super().__init__("a-image")

        try_setup_vmodel(self, preview_visible_value, prop_name="preview-visible")
        self.props(handle_props(kwargs))  # type: ignore

    def on_preview_visible_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "preview-visible-change",
            handler,
            extends=extends,
        )
        return self
