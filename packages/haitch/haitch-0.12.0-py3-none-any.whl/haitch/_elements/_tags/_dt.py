from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DescriptionTermElement = NewType("DescriptionTermElement", Element)
"""A `<dt>` element."""


def dt(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> DescriptionTermElement:
    """Specifies a term in a description or definition list.

    It is usually followed by a `dd` element; however, multiple `dt` elements in
    a row indicate several terms that are all defined by the immediate next `dd`
    element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dt>
    """
    el = Element("dt")(**attrs, **extra_attrs or {})(*children)
    return DescriptionTermElement(el)
