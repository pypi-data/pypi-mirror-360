__all__ = [
    "span",
    "label",
    "paragraph",
    "input",
    "number",
    "button",
    "checkbox",
    "radio",
    "form",
    "select",
    "option",
    "ul",
    "li",
    "div",
    "range",
    "date",
    "link",
    "textarea",
    "table",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]

from .span import Span as span
from .label import Label as label
from .paragraph import Paragraph as paragraph
from .input import Input as input
from .number import Number as number
from .button import Button as button
from .checkbox import Checkbox as checkbox
from .radio import Radio as radio
from .form import Form as form
from .select import Select as select
from .ul import Ul as ul
from .li import Li as li
from .div import Div as div
from .range import Range as range
from .date import Date as date
from .link import Link as link
from .textarea import Textarea as textarea
from .table import Table as table
from .heading import H1 as h1, H2 as h2, H3 as h3, H4 as h4, H5 as h5, H6 as h6

option = select.Option

from . import _preset  # noqa: E402, F401
