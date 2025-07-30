import typing
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element


class TabPane(Element):
    def __init__(self, *, key: str, title: typing.Optional[TMaybeRef[str]] = None):
        super().__init__("a-tab-pane")

        self.key(key)
        if title is not None:
            self.props({"title": title})
