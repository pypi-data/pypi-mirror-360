from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TfootElement = NewType("TfootElement", Element)
"""A `<tfoot>` element."""


def tfoot(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> TfootElement:
    """Indicates that table rows comprise the foot of a table.

    This is usually a summary of the columns, e.g., a sum of the given numbers
    in a column.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tfoot>
    """
    el = Element("tfoot")(**attrs, **extra_attrs or {})(*children)
    return TfootElement(el)
