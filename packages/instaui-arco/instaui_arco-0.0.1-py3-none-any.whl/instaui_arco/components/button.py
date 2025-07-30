from __future__ import annotations
import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui.components.content import Content
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Button(Element):
    def __init__(
        self,
        label: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TButton],
    ):
        """Create a button element.

        Args:
            text (Optional[TMaybeRef[str]], optional): _description_. Defaults to None.
        """

        super().__init__("a-button")

        if label is not None:
            with self:
                Content(label)

        self.props(handle_props(kwargs))  # type: ignore

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "click",
            handler,
            extends=extends,
        )
        return self
