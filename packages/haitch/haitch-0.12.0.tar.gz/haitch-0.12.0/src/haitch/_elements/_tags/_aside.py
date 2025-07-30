from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

AsideElement = NewType("AsideElement", Element)
"""An `<aside>` element."""


def aside(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> AsideElement:
    """Represents a portion whose content is only indirectly related.

    Asides are frequently presented as sidebars or call-out boxes.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/aside>
    """
    el = Element("aside")(**attrs, **extra_attrs or {})(*children)
    return AsideElement(el)
