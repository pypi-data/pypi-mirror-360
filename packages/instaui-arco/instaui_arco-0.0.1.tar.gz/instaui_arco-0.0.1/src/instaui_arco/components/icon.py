from __future__ import annotations
import typing
from instaui import ui
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui.vars.mixin_types.element_binding import ElementBindingMixin


class Icon(Element):
    def __init__(self, name: typing.Optional[TMaybeRef[str]] = None):
        if isinstance(name, ElementBindingMixin):
            name = ui.str_format(r"a-icon-{}", name)

        else:
            name = f"a-icon-{name}"

        super().__init__(name)
