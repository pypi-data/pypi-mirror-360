from typing import Callable, Dict, Optional, Union, cast
from instaui import ui
from instaui_arco.types import TLocale, TCustomizeLocale
from instaui_arco.components.config_provider import ConfigProvider
from instaui_arco.locales import get_locale


_STOP_LIFESPAN: Optional[Callable] = None


def configure(*, locale: ui.TMaybeRef[Union[TLocale, TCustomizeLocale]]):
    global _STOP_LIFESPAN

    if isinstance(locale, str):
        locale = get_locale(locale)

    def add_config_provider_lifespan():
        with ConfigProvider(locale=cast(Dict, locale)):
            yield

    if _STOP_LIFESPAN is not None:
        _STOP_LIFESPAN()
        del _STOP_LIFESPAN

    _STOP_LIFESPAN = ui.on_page_request_lifespan(add_config_provider_lifespan)
