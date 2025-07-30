from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

RubyElement = NewType("RubyElement", Element)
"""A `<ruby>` element."""


def ruby(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> RubyElement:
    """Represents small annotations above, below, or next to base text.

    This is usually for showing the pronunciation of East Asian characters. It
    can also be used for annotating other kinds of text, but this usage is less
    common.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ruby>
    """
    el = Element("ruby")(**attrs, **extra_attrs or {})(*children)
    return RubyElement(el)
