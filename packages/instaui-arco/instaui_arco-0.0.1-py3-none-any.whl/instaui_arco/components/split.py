import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Split(Element):
    def __init__(
        self,
        size_value: typing.Optional[TMaybeRef[typing.Union[int, float, str]]] = None,
        **kwargs: Unpack[component_types.TSplit],
    ):
        """Split element.


        Example:
        .. code-block:: python
            with arco.split(direction="vertical").props("max=0.8 min=0.2") as split:
                with split.first():
                    html.paragraph("first")
                with split.second():
                    html.paragraph("second")
        """

        super().__init__("a-split")

        try_setup_vmodel(self, size_value, prop_name="size")
        self.props(handle_props(kwargs))  # type: ignore

    def first(self):
        return self.add_slot("first")

    def second(self):
        return self.add_slot("second")

    def on_move_start(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "move-start",
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

    def on_move_end(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "move-end",
            handler,
            extends=extends,
        )
        return self
