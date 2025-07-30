from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TitleElement = NewType("TitleElement", Element)
"""A `<title>` element."""


def title(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> TitleElement:
    """Defines the document's title.

    The content of the title is shown in a browser's title bar or page's tab.

    Note: it only contains text; tags within the element are ignored.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/title>
    """
    el = Element("title")(**attrs, **extra_attrs or {})(*children)
    return TitleElement(el)
