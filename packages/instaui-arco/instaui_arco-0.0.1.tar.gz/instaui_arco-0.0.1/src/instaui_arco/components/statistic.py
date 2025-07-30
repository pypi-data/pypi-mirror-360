from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from ._utils import handle_props


class Statistic(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TStatistic],
    ):
        super().__init__("a-statistic")

        self.props(handle_props(kwargs))  # type: ignore
