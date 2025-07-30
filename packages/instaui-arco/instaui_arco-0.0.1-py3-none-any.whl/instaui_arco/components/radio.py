from __future__ import annotations
import typing
from typing_extensions import Unpack
import pydantic
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.vars.state import StateModel
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props
from .radio_group import RadioGroup

_TValue = typing.Union[str, float]


class Radio(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[_TValue]] = None,
        **kwargs: Unpack[component_types.TRadio],
    ):
        super().__init__("a-radio")

        self.props({"value": value})
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

    @staticmethod
    def from_list(options: TMaybeRef[typing.List[_TValue]], value: TMaybeRef[_TValue]):
        return RadioGroup(value=value, options=options)  # type: ignore

    @staticmethod
    def from_options(
        options: TMaybeRef[typing.List[RadioOption]], value: TMaybeRef[_TValue]
    ):
        return RadioGroup(value=value, options=options)  # type: ignore

    class RadioOption(StateModel):
        label: str
        value: typing.Union[str, int]
        disabled: bool = pydantic.Field(default=False)
