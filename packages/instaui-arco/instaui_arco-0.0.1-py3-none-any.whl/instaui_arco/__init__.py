"""
Easy to use arco.design for InstaUI.

Examples:
.. code-block:: python
    from instaui import ui, arco

    arco.use()

    @ui.page("/")
    def index_page():
        arco.input(placeholder="input")
"""

__all__ = [
    "use",
    "layout_header",
    "layout_footer",
    "layout_content",
    "layout_sider",
    "button",
    "icon",
    "link",
    "typography",
    "typography_title",
    "typography_paragraph",
    "divider",
    "layout",
    "space",
    "avatar",
    "badge",
    "calendar",
    "card",
    "carousel",
    "collapse",
    "comment",
    "descriptions",
    "empty",
    "image",
    "list",
    "popover",
    "statistic",
    "table",
    "tabs",
    "tag",
    "timeline",
    "tooltip",
    "tree",
    "auto_complete",
    "cascader",
    "checkbox",
    "color_picker",
    "date_picker",
    "form",
    "input",
    "input_password",
    "input_search",
    "input_number",
    "verification_code",
    "input_tag",
    "mention",
    "radio",
    "rate",
    "select",
    "slider",
    "switch",
    "textarea",
    "time_picker",
    "transfer",
    "tree_select",
    "upload",
    "alert",
    "drawer",
    "modal",
    "pop_confirm",
    "progress",
    "result",
    "spin",
    "skeleton",
    "breadcrumb",
    "dropdown",
    "menu",
    "menu_item",
    "sub_menu",
    "page_header",
    "pagination",
    "steps",
    "affix",
    "anchor",
    "back_top",
    "resize_box",
    "trigger",
    "split",
    "overflow_list",
    "watermark",
    "radio_group",
    "tab_pane",
    "config_provider",
    "use_locale",
]


from .setup import use
from .components.button import Button as button
from .components.icon import Icon as icon
from .components.link import Link as link
from .components.typography import (
    Typography as typography,
    TypographyTitle as typography_title,
    TypographyParagraph as typography_paragraph,
)
from .components.divider import Divider as divider
from .components.layout import Layout as layout
from .components.space import Space as space
from .components.avatar import Avatar as avatar
from .components.badge import Badge as badge
from .components.calendar import Calendar as calendar
from .components.card import Card as card
from .components.carousel import Carousel as carousel
from .components.collapse import Collapse as collapse
from .components.comment import Comment as comment
from .components.descriptions import Descriptions as descriptions
from .components.empty import Empty as empty
from .components.image import Image as image
from .components.list import List as list
from .components.popover import Popover as popover
from .components.statistic import Statistic as statistic
from .components.table import Table as table
from .components.tabs import Tabs as tabs
from .components.tag import Tag as tag
from .components.timeline import Timeline as timeline
from .components.tooltip import Tooltip as tooltip
from .components.tree import Tree as tree
from .components.auto_complete import AutoComplete as auto_complete
from .components.cascader import Cascader as cascader
from .components.checkbox import Checkbox as checkbox
from .components.color_picker import ColorPicker as color_picker
from .components.date_picker import DatePicker as date_picker
from .components.form import Form as form
from .components.input import Input as input
from .components.input_password import InputPassword as input_password
from .components.input_search import InputSearch as input_search
from .components.input_number import InputNumber as input_number
from .components.verification_code import VerificationCode as verification_code
from .components.input_tag import InputTag as input_tag
from .components.mention import Mention as mention
from .components.radio import Radio as radio
from .components.rate import Rate as rate
from .components.select import Select as select
from .components.slider import Slider as slider
from .components.switch import Switch as switch
from .components.textarea import Textarea as textarea
from .components.time_picker import TimePicker as time_picker
from .components.transfer import Transfer as transfer
from .components.tree_select import TreeSelect as tree_select
from .components.upload import Upload as upload
from .components.alert import Alert as alert
from .components.drawer import Drawer as drawer
from .components.modal import Modal as modal
from .components.pop_confirm import PopConfirm as pop_confirm
from .components.progress import Progress as progress
from .components.result import Result as result
from .components.spin import Spin as spin
from .components.skeleton import Skeleton as skeleton
from .components.breadcrumb import Breadcrumb as breadcrumb
from .components.dropdown import Dropdown as dropdown
from .components.menu import (
    Menu as menu,
    MenuItem as menu_item,
    SubMenu as sub_menu,
)
from .components.page_header import PageHeader as page_header
from .components.pagination import Pagination as pagination
from .components.steps import Steps as steps
from .components.affix import Affix as affix
from .components.anchor import Anchor as anchor
from .components.back_top import BackTop as back_top
from .components.config_provider import ConfigProvider as config_provider
from .components.resize_box import ResizeBox as resize_box
from .components.trigger import Trigger as trigger
from .components.split import Split as split
from .components.overflow_list import OverflowList as overflow_list
from .components.watermark import Watermark as watermark

from .components.layout_header import LayoutHeader as layout_header
from .components.layout_footer import LayoutFooter as layout_footer
from .components.layout_content import LayoutContent as layout_content
from .components.layout_sider import LayoutSider as layout_sider
from .components.radio_group import RadioGroup as radio_group
from .components.tab_pane import TabPane as tab_pane
from ._use_tools.locale import use_locale
