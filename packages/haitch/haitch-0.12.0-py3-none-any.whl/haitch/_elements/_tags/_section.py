from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SectionElement = NewType("SectionElement", Element)
"""A `<section>` element."""


def section(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SectionElement:
    """Represents a generic standalone section of a document.

    Sections should always have a heading, with very few exceptions. It should
    only be used if there isn't a more specific element to represent it.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section>
    """
    el = Element("section")(**attrs, **extra_attrs or {})(*children)
    return SectionElement(el)
