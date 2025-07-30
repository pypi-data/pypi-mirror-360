from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

FigcaptionElement = NewType("FigcaptionElement", Element)
"""A `<figcaption>` element."""


def figcaption(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> FigcaptionElement:
    """Represents a caption/legend describing the contents of parent figure.

    Nesting this in a figure element improves accessibility.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/figcaption>
    """
    el = Element("figcaption")(**attrs, **extra_attrs or {})(*children)
    return FigcaptionElement(el)
