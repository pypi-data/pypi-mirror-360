from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

LiElement = NewType("LiElement", Element)
"""A `<li>` element."""


def li(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[LiAttrs],
) -> LiElement:
    """Represents a list item.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li>
    """
    el = Element("li")(**attrs, **extra_attrs or {})(*children)
    return LiElement(el)


class LiAttrs(GlobalAttrs):
    """Attributes for the `<li>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li#attributes>
    """

    value: NotRequired[int]
    """Indicates the current ordinal value of the list item.

    The only allowed value for this attribute is a number, even if the list is
    displayed with Roman numerals or letters. List items that follow this one
    continue numbering from the value set. The value attribute has no meaning
    for unordered lists (`<ul>`) or for menus (`<menu>`).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/li#value>
    """
