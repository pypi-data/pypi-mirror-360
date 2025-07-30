from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

MenuElement = NewType("MenuElement", Element)
"""A `<menu>` element."""


def menu(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> MenuElement:
    """Semantic alternative for unordered lists.

    Treated by the browser the same as the `ul` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/menu>
    """
    el = Element("menu")(**attrs, **extra_attrs or {})(*children)
    return MenuElement(el)
