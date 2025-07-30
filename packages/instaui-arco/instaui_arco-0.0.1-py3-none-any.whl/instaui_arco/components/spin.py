from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from ._utils import handle_props


class Spin(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TSpin],
    ):
        super().__init__("a-spin")

        self.props(handle_props(kwargs))  # type: ignore
