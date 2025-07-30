from pathlib import Path
from typing import Union
from instaui import ui
from instaui.dependencies.plugin_dependency import register_plugin
from instaui_arco.types import TLocale, TCustomizeLocale
from instaui_arco._settings import configure

static_folder = Path(__file__).parent / "static"

arco_css = static_folder / "instaui-arco.css"
arco_esm_js = static_folder / "instaui-arco.js"


def _register_arco():
    register_plugin("InstauiArco", esm=arco_esm_js, css=[arco_css])


def use(*, locale: ui.TMaybeRef[Union[TLocale, TCustomizeLocale]] = "en-US"):
    """Use arco ui.

    Args:
        locale (ui.TMaybeRef[Union[TLocale, TCustomizeLocale]], optional): The locale of arco ui. Defaults to "en-US".

    Examples:
    .. code-block:: python
        from instaui import ui, arco

        arco.use()

        @ui.page("/")
        def index_page():
            arco.input(placeholder="input")
    """

    _register_arco()
    configure(locale=locale)
