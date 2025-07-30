from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

BdoElement = NewType("BdoElement", Element)
"""A `<bdo>` element."""


def bdo(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> BdoElement:
    """Overrides the current directionality of text.

    The text within is rendered in a different direction.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdo>
    """
    el = Element("bdo")(**attrs, **extra_attrs or {})(*children)
    return BdoElement(el)
