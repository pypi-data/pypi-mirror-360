from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

PreElement = NewType("PreElement", Element)
"""A `<pre>` element."""


def pre(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> PreElement:
    """Represents preformatted text presented exactly as written.

    The text is typically rendered using a non-proportional, or monospaced,
    font. Whitespace inside this element is displayed as written.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/pre>
    """
    el = Element("pre")(**attrs, **extra_attrs or {})(*children)
    return PreElement(el)
