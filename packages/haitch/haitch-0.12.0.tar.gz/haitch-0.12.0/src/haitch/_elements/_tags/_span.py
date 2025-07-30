from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SpanElement = NewType("SpanElement", Element)
"""A `<span>` element."""


def span(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SpanElement:
    """Generic inline container for phrasing content.

    Span does not inherently represent anything. It can be used to group
    elements for styling purposes (using the `class` or `id` attributes), or
    because they share attribute values, such as `lang`. It should be used only
    when no other semantic element is appropriate. `<span>` is very much like a
    `<div>` element, but `<div>` is a block-level element whereas a `<span>` is
    an inline-level element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/span>
    """
    el = Element("span")(**attrs, **extra_attrs or {})(*children)
    return SpanElement(el)
