import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel

_TSliderValue = typing.Union[int, float, typing.List[int], typing.List[float]]


class Slider(Element):
    def __init__(
        self,
        value: typing.Optional[
            TMaybeRef[
                typing.Union[_TSliderValue, typing.Tuple[_TSliderValue, _TSliderValue]]
            ]
        ] = None,
        **kwargs: Unpack[component_types.TSlider],
    ):
        super().__init__("a-slider")

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
