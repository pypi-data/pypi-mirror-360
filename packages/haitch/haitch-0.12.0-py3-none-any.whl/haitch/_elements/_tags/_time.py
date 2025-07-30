from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TimeElement = NewType("TimeElement", Element)
"""A `<time>` element."""


def time(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[TimeAttrs],
) -> TimeElement:
    """Represents a specific period in time.

    It may include the `datetime` attribute to translate dates into
    machine-readable format, allowing for better search engine results or custom
    feats such as reminders.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time>
    """
    el = Element("time")(**attrs, **extra_attrs or {})(*children)
    return TimeElement(el)


class TimeAttrs(GlobalAttrs):
    """Attributes for the `<time>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time#attributes>
    """

    datetime: NotRequired[str]
    """Indicates he time and/or date of the element.

    The datetime must be in one of the formats described below:

        - `2011`
        - `2011-11`
        - `2011-11-18`
        - `11-18`
        - `2011-W47`
        - `14:54`
        - `14:54:39`
        - `14:54:39.929`
        - `2011-11-18T14:54:39.929`
        - `2011-11-18 14:54:39.929`
        - `2011-11-18T14:54:39.929Z`
        - `2011-11-18T14:54:39.929-0400`
        - `2011-11-18T14:54:39.929-04:00`
        - `2011-11-18 14:54:39.929Z`
        - `2011-11-18 14:54:39.929-0400`
        - `2011-11-18 14:54:39.929-04:00`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/time#open>
    """
