from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

H1Element = NewType("H1Element", Element)
"""A `<h1>` element."""


def h1(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> H1Element:
    """Represents first level section heading.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Heading_Elements>
    """
    el = Element("h1")(**attrs, **extra_attrs or {})(*children)
    return H1Element(el)
