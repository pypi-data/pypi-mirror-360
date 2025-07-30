from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

PictureElement = NewType("PictureElement", Element)
"""A `<picture>` element."""


def picture(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> PictureElement:
    """Contains zero or more `source` elements and one `img` element.

    The purpose of this element is to offer alternative versions of an image for
    different display/device scenarios.

    The browser will consider each child `<source>` element and choose the best
    match among them. If no matches are found—or the browser doesn't support the
    `<picture>` element—the URL of the `<img>` element's `src` attribute is
    selected. The selected image is then presented in the space occupied by the
    `<img>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture>
    """
    el = Element("picture")(**attrs, **extra_attrs or {})(*children)
    return PictureElement(el)
