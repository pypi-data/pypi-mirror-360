from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

H6Element = NewType("H6Element", Element)
"""A `<h6>` element."""


def h6(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> H6Element:
    """Represents sixth level section heading.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Heading_Elements>
    """
    el = Element("h6")(**attrs, **extra_attrs or {})(*children)
    return H6Element(el)
