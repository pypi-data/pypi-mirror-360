from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DivElement = NewType("DivElement", Element)
"""A `<div>` element."""


def div(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> DivElement:
    """Generic container for flow content.

    As a "pure" container, the `<div>` element does not inherently represent
    anything. Instead, it's used to group content so it can be easily styled
    using the `class` or `id` attributes, marking a section of a document as
    being written in a different language (using the `lang` attribute), and so
    on.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div>
    """
    el = Element("div")(**attrs, **extra_attrs or {})(*children)
    return DivElement(el)
