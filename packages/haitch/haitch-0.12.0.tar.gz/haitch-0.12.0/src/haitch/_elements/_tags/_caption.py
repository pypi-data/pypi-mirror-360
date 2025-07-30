from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

CaptionElement = NewType("CaptionElement", Element)
"""A `<caption>` element."""


def caption(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> CaptionElement:
    """Specifies the caption or title of a table.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/caption>
    """
    el = Element("caption")(**attrs, **extra_attrs or {})(*children)
    return CaptionElement(el)
