import typing
from typing_extensions import Unpack, TypedDict
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class TRadioGroup(TypedDict, total=False):
    model_value: typing.Union[str, int, bool]
    default_value: typing.Union[str, int, bool]
    type: typing.Literal["radio", "button"]
    size: typing.Literal["mini", "small", "medium", "large"]
    options: typing.List[typing.Union[str, int]]
    direction: typing.Literal["horizontal", "vertical"]
    disabled: bool


class RadioGroup(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[typing.Union[str, float]]] = None,
        **kwargs: Unpack[TRadioGroup],
    ):
        super().__init__("a-radio-group")

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
