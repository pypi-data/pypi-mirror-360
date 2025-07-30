import typing
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, try_setup_vmodel


class Upload(Element):
    def __init__(
        self,
        value: typing.Optional[TMaybeRef[typing.Any]] = None,
        **kwargs: Unpack[component_types.TUpload],
    ):
        super().__init__("a-upload")

        try_setup_vmodel(self, value)
        self.props(handle_props(kwargs))  # type: ignore

    def on_submit(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "submit",
            handler,
            extends=extends,
        )
        return self

    def on_abort(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "abort",
            handler,
            extends=extends,
        )
        return self

    def on_update_file(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "updateFile",
            handler,
            extends=extends,
        )
        return self

    def on_upload(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "upload",
            handler,
            extends=extends,
        )
        return self
