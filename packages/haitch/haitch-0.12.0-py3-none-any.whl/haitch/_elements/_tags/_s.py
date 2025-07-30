from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

StrikethroughElement = NewType("StrikethroughElement", Element)
"""An `<s>` element."""


def s(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> StrikethroughElement:
    """Renders text with a strikethrough or a line through it.

    Use this element to represent things that are no longer relevant or no
    longer accurate. When indicating document edits, use the `ins` and `del`
    elements.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/s>
    """
    el = Element("s")(**attrs, **extra_attrs or {})(*children)
    return StrikethroughElement(el)
