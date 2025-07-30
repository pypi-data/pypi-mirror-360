from __future__ import annotations
from collections.abc import Sequence
import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui import ui
from instaui.components.element import Element
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


_TSelectValue = typing.Union[str, int, typing.Sequence[str], typing.Sequence[int]]

_OPTIONS_TRANSLATE_JS: typing.Final = r"""(options)=>{
    if (Array.isArray(options)){
        const obj = {};
        options.forEach(item => {
            obj[item] = item;
        });
        return obj;                             
    }
    return options;
}
"""


class Select(Element):
    def __init__(
        self,
        options: TMaybeRef[typing.Union[typing.Sequence, typing.Dict]],
        value: typing.Optional[TMaybeRef[_TSelectValue]] = None,
        **kwargs: Unpack[component_types.TSelect],
    ):
        super().__init__("a-select")

        if isinstance(options, ObservableMixin):
            options = ui.js_computed(inputs=[options], code=_OPTIONS_TRANSLATE_JS)
        else:
            options = (
                {str(i): str(i) for i in options}
                if isinstance(options, Sequence)
                else options
            )

        with self.add_slot("default"):
            with ui.vfor(options) as item:
                item = ui.iter_info(item)
                Select.Option(item.dict_value).props(
                    {"value": item.dict_key, "label": item.dict_value}
                )

        try_setup_vmodel(self, value)
        self.props(handle_props(kwargs))  # type: ignore

    class Option(Element):
        def __init__(
            self,
            text: typing.Optional[TMaybeRef[str]] = None,
        ):
            super().__init__("a-option")

            if text is not None:
                with self:
                    ui.content(text)

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

    def on_input_value_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "input-value-change",
            handler,
            extends=extends,
        )
        return self

    def on_popup_visible_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "popup-visible-change",
            handler,
            extends=extends,
        )
        return self

    def on_clear(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "clear",
            handler,
            extends=extends,
        )
        return self

    def on_remove(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "remove",
            handler,
            extends=extends,
        )
        return self

    def on_search(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "search",
            handler,
            extends=extends,
        )
        return self

    def on_dropdown_scroll(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "dropdown-scroll",
            handler,
            extends=extends,
        )
        return self

    def on_dropdown_reach_bottom(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "dropdown-reach-bottom",
            handler,
            extends=extends,
        )
        return self

    def on_exceed_limit(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "exceed-limit",
            handler,
            extends=extends,
        )
        return self
