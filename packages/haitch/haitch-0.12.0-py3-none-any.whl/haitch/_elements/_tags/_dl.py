from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DescriptionListElement = NewType("DescriptionListElement", Element)
"""A `<dl>` element."""


def dl(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> DescriptionListElement:
    """Encloses a list of groups of terms and descriptions.

    Common uses for this element are to implement a glossary or to display
    metadta (a list of key-value pairs).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl>
    """
    el = Element("dl")(**attrs, **extra_attrs or {})(*children)
    return DescriptionListElement(el)
