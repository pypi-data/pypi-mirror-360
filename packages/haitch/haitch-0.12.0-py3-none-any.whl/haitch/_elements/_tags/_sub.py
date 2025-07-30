from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SubElement = NewType("SubElement", Element)
"""A `<sub>` element."""


def sub(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SubElement:
    """Specifies inline text which should be displayed as subscript.

    This is solely for typographical reasons. Subscripts are typically rendered
    with a lowered baseline using smaller text.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/sub>
    """
    el = Element("sub")(**attrs, **extra_attrs or {})(*children)
    return SubElement(el)
