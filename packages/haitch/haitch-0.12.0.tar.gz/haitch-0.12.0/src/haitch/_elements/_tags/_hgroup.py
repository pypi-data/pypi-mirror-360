from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

HgroupElement = NewType("HgroupElement", Element)
"""A `<hgroup>` element."""


def hgroup(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> HgroupElement:
    """Represents a heading and related content.

    It groups a single `<h1>-<h6>` element with one or more `p` elements.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/hgroup>
    """
    el = Element("hgroup")(**attrs, **extra_attrs or {})(*children)
    return HgroupElement(el)
