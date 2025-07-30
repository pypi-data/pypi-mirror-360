import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props
from .tab_pane import TabPane


class Tabs(Element):
    def __init__(
        self,
        active_key: typing.Optional[TMaybeRef[typing.Union[str, int]]] = None,
        *,
        active_key_model_value: typing.Optional[typing.Union[str, int]] = None,
        **kwargs: Unpack[component_types.TTabs],
    ):
        """Tabs element.

        Example:
        .. code-block:: python
            with arco.tabs() as tabs:
                with tabs.add_pane(key="1", title="Tab 1"):
                    html.paragraph("tab 1")
                with tabs.add_pane(key="2", title="Tab 2"):
                    html.paragraph("tab 2")
                with tabs.add_pane(key="3", title="Tab 3"):
                    html.paragraph("tab 3")

        """
        super().__init__("a-tabs")
        self.props(handle_props(kwargs))  # type: ignore

        if active_key is not None:
            self.vmodel(active_key, prop_name="active-key")

        if active_key_model_value is not None:
            self.props({"active-key": active_key_model_value})

    def add_pane(self, *, key: str, title: str):
        """Add a new pane to the tabs.

        Args:
            key (str): key of the pane.
            title (str): title of the pane.

        """
        return TabPane(key=key, title=title)

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self

    def on_tab_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "tab-click",
            handler,
            extends=extends,
        )
        return self

    def on_add(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "add",
            handler,
            extends=extends,
        )
        return self

    def on_delete(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "delete",
            handler,
            extends=extends,
        )
        return self
