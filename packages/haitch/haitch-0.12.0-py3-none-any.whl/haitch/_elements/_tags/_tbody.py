from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TbodyElement = NewType("TbodyElement", Element)
"""A `<tbody>` element."""


def tbody(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> TbodyElement:
    """Indicates that table rows comprise the table's (main) data.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tbody>
    """
    el = Element("tbody")(**attrs, **extra_attrs or {})(*children)
    return TbodyElement(el)
