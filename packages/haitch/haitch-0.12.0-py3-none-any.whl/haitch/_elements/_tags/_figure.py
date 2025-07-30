from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

FigureElement = NewType("FigureElement", Element)
"""A `<figure>` element."""


def figure(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> FigureElement:
    """Represents self-contained figure content.

    The figure, its caption, and its content are referenced as a single unit. Usually
    this element nests an image, illustration, diagram, code snippet, etc.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figure>
    """
    el = Element("figure")(**attrs, **extra_attrs or {})(*children)
    return FigureElement(el)
