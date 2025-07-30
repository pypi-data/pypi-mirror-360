from typing import Dict
from instaui.components.element import Element
from instaui.vars.mixin_types.element_binding import ElementBindingMixin


def handle_props(props: Dict):
    return {k.replace("_", "-"): v for k, v in props.items()}


def try_setup_vmodel(
    element: Element,
    value,
    *,
    prop_name: str = "value",
):
    if value is None:
        return
    if isinstance(value, ElementBindingMixin):
        element.vmodel(value, prop_name=prop_name)
        return

    element.props({prop_name: value})
