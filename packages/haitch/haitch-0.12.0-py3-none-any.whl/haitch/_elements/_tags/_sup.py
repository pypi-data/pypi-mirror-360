from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SupElement = NewType("SupElement", Element)
"""A `<sup>` element."""


def sup(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SupElement:
    """Specifies inline text which should be displayed as superscript.

    This is solely for typographical reasons. Supscripts are typically rendered
    with a raised baseline using smaller text.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sup>
    """
    el = Element("sup")(**attrs, **extra_attrs or {})(*children)
    return SupElement(el)
