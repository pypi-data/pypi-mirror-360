from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

HeadElement = NewType("HeadElement", Element)
"""A `<head>` element."""


def head(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> HeadElement:
    """Contains metadata about the document.

    This usually is metadata regarding the title, scripts, and style sheets.

    Note: <head> primarily holds information for machine processing, not
    human-readability. For human-visible information, like top-level headings
    and listed authors, see the <header> element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/head>
    """
    el = Element("head")(**attrs, **extra_attrs or {})(*children)
    return HeadElement(el)
