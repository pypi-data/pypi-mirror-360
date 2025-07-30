import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Table(Element):
    def __init__(
        self,
        **kwargs: Unpack[component_types.TTable],
    ):
        super().__init__("a-table")

        self.props(handle_props(kwargs))  # type: ignore

    def on_expand(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "expand",
            handler,
            extends=extends,
        )
        return self

    def on_expanded_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "expanded-change",
            handler,
            extends=extends,
        )
        return self

    def on_select(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "select",
            handler,
            extends=extends,
        )
        return self

    def on_select_all(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "select-all",
            handler,
            extends=extends,
        )
        return self

    def on_selection_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "selection-change",
            handler,
            extends=extends,
        )
        return self

    def on_sorter_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "sorter-change",
            handler,
            extends=extends,
        )
        return self

    def on_filter_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "filter-change",
            handler,
            extends=extends,
        )
        return self

    def on_page_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "page-change",
            handler,
            extends=extends,
        )
        return self

    def on_page_size_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "page-size-change",
            handler,
            extends=extends,
        )
        return self

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

    def on_cell_mouse_enter(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-mouse-enter",
            handler,
            extends=extends,
        )
        return self

    def on_cell_mouse_leave(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-mouse-leave",
            handler,
            extends=extends,
        )
        return self

    def on_cell_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-click",
            handler,
            extends=extends,
        )
        return self

    def on_row_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "row-click",
            handler,
            extends=extends,
        )
        return self

    def on_header_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "header-click",
            handler,
            extends=extends,
        )
        return self

    def on_column_resize(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "column-resize",
            handler,
            extends=extends,
        )
        return self

    def on_row_dblclick(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "row-dblclick",
            handler,
            extends=extends,
        )
        return self

    def on_cell_dblclick(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-dblclick",
            handler,
            extends=extends,
        )
        return self

    def on_row_contextmenu(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "row-contextmenu",
            handler,
            extends=extends,
        )
        return self

    def on_cell_contextmenu(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cell-contextmenu",
            handler,
            extends=extends,
        )
        return self
