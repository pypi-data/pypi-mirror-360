from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

CanvasElement = NewType("CanvasElement", Element)
"""A `<canvas>` element."""


def canvas(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[CanvasAttrs],
) -> CanvasElement:
    """Draw graphics and animations.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas>
    """
    el = Element("canvas")(**attrs, **extra_attrs or {})(*children)
    return CanvasElement(el)


class CanvasAttrs(GlobalAttrs):
    """Attributes for the `<canvas>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas#attributes>
    """

    height: NotRequired[int]
    """The height of the coordinate space in CSS pixels (default: 150).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas#height>
    """

    width: NotRequired[int]
    """The width of the coordinate space in CSS pixels (default: 300).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas#width>
    """
