from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

MarkElement = NewType("MarkElement", Element)
"""A `<mark>` element."""


def mark(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> MarkElement:
    """Represents text which highlighted for reference/notation purposes.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/mark>
    """
    el = Element("mark")(**attrs, **extra_attrs or {})(*children)
    return MarkElement(el)
