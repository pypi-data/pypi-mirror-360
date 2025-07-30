from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

RubyTextElement = NewType("RubyTextElement", Element)
"""A `<rt>` element."""


def rt(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> RubyTextElement:
    """Specifies the ruby text component of a ruby annotation.

    This is used to provide pronunciation, translation, or transliteration
    information for East Asian typography. This element must always be contained
    with a `ruby` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/rt>
    """
    el = Element("rt")(**attrs, **extra_attrs or {})(*children)
    return RubyTextElement(el)
