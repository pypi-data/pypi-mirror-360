from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

UlElement = NewType("UlElement", Element)
"""A `<ul>` element."""


def ul(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> UlElement:
    """Represents an unordered list of items.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ul>
    """
    el = Element("ul")(**attrs, **extra_attrs or {})(*children)
    return UlElement(el)
