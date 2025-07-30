import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Input(Element):
    _exten_name: typing.ClassVar[typing.Optional[str]] = None

    def __init__(
        self,
        value: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TInput],
    ):
        tag = f"a-input{'-' + self._exten_name if self._exten_name else ''}"
        super().__init__(tag)
        try_setup_vmodel(self, value)
        self.props(handle_props(kwargs))  # type: ignore

    def __init_subclass__(cls, *, exten_name: str = "") -> None:
        cls._exten_name = exten_name

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

    def on_press_enter(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "press-enter",
            handler,
            extends=extends,
        )
        return self

    def on_clear(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "clear",
            handler,
            extends=extends,
        )
        return self

    def on_focus(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "focus",
            handler,
            extends=extends,
        )
        return self

    def on_blur(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "blur",
            handler,
            extends=extends,
        )
        return self
