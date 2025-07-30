from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

HrElement = NewType("HrElement", VoidElement)
"""An `<hr>` element."""


def hr(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> HrElement:
    """Represents a thematic break between paragraph-level elements.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hr>
    """
    el = VoidElement("hr")(**attrs, **extra_attrs or {})
    return HrElement(el)
