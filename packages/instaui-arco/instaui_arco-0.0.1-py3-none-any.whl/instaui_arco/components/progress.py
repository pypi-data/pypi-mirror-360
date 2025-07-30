from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from ._utils import handle_props


class Progress(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TProgress],
    ):
        super().__init__("a-progress")

        self.props(handle_props(kwargs))  # type: ignore
