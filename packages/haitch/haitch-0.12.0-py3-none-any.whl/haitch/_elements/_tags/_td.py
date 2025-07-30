from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TdElement = NewType("TdElement", Element)
"""A `<td>` element."""


def td(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> TdElement:
    """Defines a cell of a table that contains data.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/td>
    """
    el = Element("td")(**attrs, **extra_attrs or {})(*children)
    return TdElement(el)
