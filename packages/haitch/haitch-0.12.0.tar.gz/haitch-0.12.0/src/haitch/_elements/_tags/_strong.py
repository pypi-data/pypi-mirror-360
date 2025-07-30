from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

StrongElement = NewType("StrongElement", Element)
"""A `<strong>` element."""


def strong(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> StrongElement:
    """Indicates the content has strong importance, seriousness, or urgency.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/strong>
    """
    el = Element("strong")(**attrs, **extra_attrs or {})(*children)
    return StrongElement(el)
