from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

FooterElement = NewType("FooterElement", Element)
"""A `<footer>` element."""


def footer(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> FooterElement:
    """Represents a footer for its nearest ancestor content or root element.

    A `<footer>` typically contains information about the author of the section,
    copyright data or links to related documents.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/footer>
    """
    el = Element("footer")(**attrs, **extra_attrs or {})(*children)
    return FooterElement(el)
