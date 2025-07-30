from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

EmElement = NewType("EmElement", Element)
"""An `<em>` element."""


def em(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> EmElement:
    """Marks text that has stress emphasis.

    These elements can be nested, with each level of nesting indicating a
    greated degree of emphasis.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/em>
    """
    el = Element("em")(**attrs, **extra_attrs or {})(*children)
    return EmElement(el)
