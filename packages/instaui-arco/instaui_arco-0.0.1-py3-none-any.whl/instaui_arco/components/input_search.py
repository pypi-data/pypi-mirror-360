import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from .input import Input


class TInputSearch(component_types.TInput):
    search_button: bool
    loading: bool
    disabled: bool
    size: typing.Literal["mini", "small", "medium", "large"]
    button_text: str
    button_props: typing.Dict[str, typing.Any]


class InputSearch(Input, exten_name="search"):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[TInputSearch],
    ):
        super().__init__(value=value, **kwargs)

    def on_search(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "search",
            handler,
            extends=extends,
        )
        return self
