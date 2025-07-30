from __future__ import annotations
from typing import List, Optional
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Link(Element):
    def __init__(
        self,
        text: Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TLink],
    ):
        super().__init__("a-link")

        if text is not None:
            self.props({"text": text})

        self.props(handle_props(kwargs))  # type: ignore

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
        key: Optional[str] = None,
    ):
        self.on(
            "click",
            handler,
            extends=extends,
        )
        return self
