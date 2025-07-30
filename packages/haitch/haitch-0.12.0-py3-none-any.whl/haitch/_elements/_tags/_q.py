from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

QuoteElement = NewType("QuoteElement", Element)
"""A `<q>` element."""


def q(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[QuoteAttrs],
) -> QuoteElement:
    """Indicates that the enclosed text is short inline quotation.

    Most modern browsers indicate this by sorrounding the text in quotation
    marks. This element is intended for short quotations that don't require
    paragraph breaks; for long quotations, use the `blockquote` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/q>
    """
    el = Element("q")(**attrs, **extra_attrs or {})(*children)
    return QuoteElement(el)


class QuoteAttrs(GlobalAttrs):
    """Attributes for the `<q>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/q#attributes>
    """

    cite: NotRequired[str]
    """A URL that designates a source for the information quoted.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/q#cite>
    """
