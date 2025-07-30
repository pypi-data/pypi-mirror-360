from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

IElement = NewType("IElement", Element)
"""An `<i>` element."""


def i(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> IElement:
    """Reperents a range of text that is set off from the normal text.

    Example use-cases for this element idiomatic text, technical terms,
    taxonomical designations, among others. Historically, these have been
    presented using italicized type, which is the original source the `i` naming
    of this element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/i>
    """
    el = Element("i")(**attrs, **extra_attrs or {})(*children)
    return IElement(el)
