from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

BElement = NewType("BElement", Element)
"""A `<b>` element."""


def b(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> BElement:
    """Draws attention to the element's contents.

    This was formerly known as the Boldface element, and most browsers still
    draw the text in boldface. However, you should not use `<b>` for styling
    text or granting importance. If you wish to create boldface text, you should
    use the CSS `font-weight` property. If you wish to indicate an element is of
    special importance, you should use the `<strong>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/b>
    """
    el = Element("b")(**attrs, **extra_attrs or {})(*children)
    return BElement(el)
