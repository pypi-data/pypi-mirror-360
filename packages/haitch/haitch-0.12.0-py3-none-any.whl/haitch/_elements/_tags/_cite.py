from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

CiteElement = NewType("CiteElement", Element)
"""A `<cite>` element."""


def cite(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> CiteElement:
    """Marks up the title of a creative work.

    The reference may be in an abbreviated form according to context-appropriate
    conventions related to citation metadata.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/cite>
    """
    el = Element("cite")(**attrs, **extra_attrs or {})(*children)
    return CiteElement(el)
