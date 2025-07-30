import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel

_TResizeBoxSizeValue = typing.Union[int, float]


class ResizeBox(Element):
    def __init__(
        self,
        width_value: typing.Optional[TMaybeRef[_TResizeBoxSizeValue]] = None,
        height_value: typing.Optional[TMaybeRef[_TResizeBoxSizeValue]] = None,
        **kwargs: Unpack[component_types.TResizebox],
    ):
        super().__init__("a-resize-box")

        try_setup_vmodel(self, width_value, prop_name="width")
        try_setup_vmodel(self, height_value, prop_name="height")
        self.props(handle_props(kwargs))  # type: ignore

    def on_moving_start(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "moving-start",
            handler,
            extends=extends,
        )
        return self

    def on_moving(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "moving",
            handler,
            extends=extends,
        )
        return self

    def on_moving_end(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "moving-end",
            handler,
            extends=extends,
        )
        return self
