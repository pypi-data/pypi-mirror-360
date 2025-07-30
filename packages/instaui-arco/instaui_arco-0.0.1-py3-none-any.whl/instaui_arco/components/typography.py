from __future__ import annotations
import typing
from typing_extensions import Unpack
from instaui.vars.types import TMaybeRef
from instaui.components.element import Element
from instaui.components.content import Content
from instaui_arco import component_types
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props


class Typography(Element):
    _exten_name: typing.ClassVar[typing.Optional[str]] = None

    def __init__(
        self,
        text: typing.Optional[TMaybeRef[str]] = None,
        **kwargs: Unpack[component_types.TTypography],
    ):
        tag = f"a-typography{'-' + self._exten_name if self._exten_name else ''}"
        super().__init__(tag)

        if text is not None:
            with self:
                Content(text)

        self.props(handle_props(kwargs))  # type: ignore

    def __init_subclass__(cls, *, exten_name: str = "") -> None:
        cls._exten_name = exten_name

    def on_edit_start(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "edit-start",
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

    def on_edit_end(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "edit-end",
            handler,
            extends=extends,
        )
        return self

    def on_copy(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "copy",
            handler,
            extends=extends,
        )
        return self

    def on_ellipsis(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "ellipsis",
            handler,
            extends=extends,
        )
        return self

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


class TypographyTitle(Typography, exten_name="title"):
    def __init__(
        self,
        text: typing.Optional[TMaybeRef[str]] = None,
        *,
        heading: typing.Optional[
            TMaybeRef[typing.Literal["1", "2", "3", "4", "5", "6"]]
        ] = None,
        **kwargs: Unpack[component_types.TTypography],
    ):
        super().__init__(text=text, **kwargs)

        if heading is not None:
            self.props({"heading": heading})


class TypographyParagraph(Typography, exten_name="paragraph"):
    def __init__(
        self,
        text: typing.Optional[TMaybeRef[str]] = None,
        *,
        blockquote: typing.Optional[TMaybeRef[bool]] = None,
        spacing: typing.Optional[TMaybeRef[typing.Literal["default", "close"]]] = None,
        **kwargs: Unpack[component_types.TTypography],
    ):
        super().__init__(text=text, **kwargs)

        if blockquote is not None:
            self.props({"blockquote": blockquote})

        if spacing is not None:
            self.props({"spacing": spacing})
