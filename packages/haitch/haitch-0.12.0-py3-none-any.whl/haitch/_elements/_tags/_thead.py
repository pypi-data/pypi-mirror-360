from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TheadElement = NewType("TheadElement", Element)
"""A `<thead>` element."""


def thead(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> TheadElement:
    """Indicates that table rows comprise the table's columns.

    This is usually in the form of column headers (`th` elements).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/thead>
    """
    el = Element("thead")(**attrs, **extra_attrs or {})(*children)
    return TheadElement(el)
