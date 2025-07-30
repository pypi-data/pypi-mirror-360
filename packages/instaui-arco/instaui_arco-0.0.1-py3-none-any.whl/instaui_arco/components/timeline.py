from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from ._utils import handle_props


class Timeline(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TTimeline],
    ):
        super().__init__("a-timeline")

        self.props(handle_props(kwargs))  # type: ignore
