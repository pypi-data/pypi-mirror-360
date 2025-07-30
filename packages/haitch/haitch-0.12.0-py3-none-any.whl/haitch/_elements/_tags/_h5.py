from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

H5Element = NewType("H5Element", Element)
"""A `<h5>` element."""


def h5(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> H5Element:
    """Represents fifth level section heading.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Heading_Elements>
    """
    el = Element("h5")(**attrs, **extra_attrs or {})(*children)
    return H5Element(el)
