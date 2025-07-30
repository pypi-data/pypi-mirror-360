from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

WbrElement = NewType("WbrElement", VoidElement)
"""A `<wbr>` element."""


def wbr(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> WbrElement:
    """Represents a word break opportunity.

    This is a position within text where the browser may optionally break a
    line, though its line-breaking rules would not otherwise create a break at
    that location

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/wbr>
    """
    el = VoidElement("wbr")(**attrs, **extra_attrs or {})
    return WbrElement(el)
