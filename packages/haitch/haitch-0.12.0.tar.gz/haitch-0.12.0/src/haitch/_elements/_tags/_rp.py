from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

RubyParenthesesElement = NewType("RubyParenthesesElement", Element)
"""A `<rp>` element."""


def rp(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> RubyParenthesesElement:
    """Provides fall-back parentheses for ruby annotations.

    This is to protect against browsers that do not support display of ruby
    annotations. One `rp` element should enclose each of the opening and closing
    parentheses that wrap the `rt` element that contains the annotation's text.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/rp>
    """
    el = Element("rp")(**attrs, **extra_attrs or {})(*children)
    return RubyParenthesesElement(el)
