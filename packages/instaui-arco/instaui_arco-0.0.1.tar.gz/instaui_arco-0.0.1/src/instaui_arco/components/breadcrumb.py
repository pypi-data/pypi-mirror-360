from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from ._utils import handle_props


class Breadcrumb(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TBreadcrumb],
    ):
        super().__init__("a-breadcrumb")

        self.props(handle_props(kwargs))  # type: ignore
