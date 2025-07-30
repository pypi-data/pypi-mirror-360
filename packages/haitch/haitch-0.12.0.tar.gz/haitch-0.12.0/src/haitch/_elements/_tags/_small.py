from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SmallElement = NewType("SmallElement", Element)
"""A `<small>` element."""


def small(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SmallElement:
    """Represents side-comments and small print.

    Common examples are copyright and legal text.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/small>
    """
    el = Element("small")(**attrs, **extra_attrs or {})(*children)
    return SmallElement(el)
