from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

BlockquoteElement = NewType("BlockquoteElement", Element)
"""A `<blockquote>` element."""


def blockquote(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[BlockquoteAttrs],
) -> BlockquoteElement:
    """Indicates that the enclosed text is an extended quotation.

    Usually, this is rendered visually by indentation. A URL for the source of
    the quotation may be given using the `cite` attribute, while a text
    representation of the source can be given using the `cite` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blockquote>
    """
    el = Element("blockquote")(**attrs, **extra_attrs or {})(*children)
    return BlockquoteElement(el)


class BlockquoteAttrs(GlobalAttrs):
    """Attributes for the `<blockquote>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blockquote#attributes>
    """

    cite: NotRequired[str]
    """A URL that designates a source for the information quoted.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/blockquote#cite>
    """
