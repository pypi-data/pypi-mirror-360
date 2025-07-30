from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from ._utils import handle_props


class ConfigProvider(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TConfigprovider],
    ):
        super().__init__("a-config-provider")
        self.props(handle_props(kwargs))  # type: ignore
