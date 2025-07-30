from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ColgroupElement = NewType("ColgroupElement", Element)
"""A `<colgroup>` element."""


def colgroup(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ColgroupAttrs],
) -> ColgroupElement:
    """Defines a group of columns within a table.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup>
    """
    el = Element("colgroup")(**attrs, **extra_attrs or {})(*children)
    return ColgroupElement(el)


class ColgroupAttrs(GlobalAttrs):
    """Attributes for the `<colgroup>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup#attributes>
    """

    span: NotRequired[int]
    """Specifies the number of consecutive columns to span.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup#span>
    """
