from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

BrElement = NewType("BrElement", VoidElement)
"""A `<br>` element."""


def br(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> BrElement:
    """Produces a line break in text (carriage-return).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/br>
    """
    el = VoidElement("br")(**attrs, **extra_attrs or {})
    return BrElement(el)
