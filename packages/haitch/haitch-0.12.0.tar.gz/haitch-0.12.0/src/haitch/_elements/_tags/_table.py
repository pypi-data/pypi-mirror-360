from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TableElement = NewType("TableElement", Element)
"""A `<table>` element."""


def table(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> TableElement:
    """Represents tabular data.

    Following elements are part of the table structure:

        - `<caption>`
        - `<thead>`
        - `<colgroup>`
        - `<col>`
        - `<th>`
        - `<tbody>`
        - `<tr>`
        - `<td>`
        - `<tfoot>`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table>
    """
    el = Element("table")(**attrs, **extra_attrs or {})(*children)
    return TableElement(el)
