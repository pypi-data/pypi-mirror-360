from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

BdiElement = NewType("BdiElement", Element)
"""A `<bdi>` element."""


def bdi(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> BdiElement:
    """Treats the text it contains in isolation from its sorrounding text.

    It's particularly useful when a website dynamically inserts some text and
    doesn't know the directionality of the text being inserted. Note: the `dir`
    attribute behavaves differently than normal: it defaults to `auto`, meaning
    its value is never inherited from the parent element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/bdi>
    """
    el = Element("bdi")(**attrs, **extra_attrs or {})(*children)
    return BdiElement(el)
