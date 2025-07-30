from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

NavElement = NewType("NavElement", Element)
"""A `<nav>` element."""


def nav(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> NavElement:
    """Represents a section whose purpose is to provide navigation links.

    Common examples of navigation sections are menus, tables of contents, and
    indexes. A document may have several `<nav>` elements.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nav>
    """
    el = Element("nav")(**attrs, **extra_attrs or {})(*children)
    return NavElement(el)
