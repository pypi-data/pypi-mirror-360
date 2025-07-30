from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

KbdElement = NewType("KbdElement", Element)
"""A `<kbd>` element."""


def kbd(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> KbdElement:
    """Represents a span of inline text denoting user input.

    Example inputs are keyboard, voice input, or any other text entry device.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/kbd>
    """
    el = Element("kbd")(**attrs, **extra_attrs or {})(*children)
    return KbdElement(el)
