from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

OlElement = NewType("OlElement", Element)
"""A `<ol>` element."""


def ol(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[OlAttrs],
) -> OlElement:
    """Represents an ordered list of items.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol>
    """
    el = Element("ol")(**attrs, **extra_attrs or {})(*children)
    return OlElement(el)


class OlAttrs(GlobalAttrs):
    """Attributes for the `<ol>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol#attributes>
    """

    reversed: NotRequired[bool]
    """Specifies that the list's items are in reverse order.

    Items will be numbered from high to low.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol#reversed>
    """

    start: NotRequired[int]
    """An integer to start counting from for the list items.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol#reversed>
    """

    type_: NotRequired[Literal["a", "A", "i", "I", "1"]]
    """Sets the numbering type.

    Available numbering types:
        - `a` for lowercase letters
        - `A` for uppercase letters
        - `i` for lowercase Roman numerals
        - `I` for uppercase Roman numerals
        - `1` for numbers (default)

    Note: Unless the type of the list number matters (like legal or technical documents
    where items are referenced by their number/letter), use the CSS `list-style-type`
    property instead.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ol#type>
    """
