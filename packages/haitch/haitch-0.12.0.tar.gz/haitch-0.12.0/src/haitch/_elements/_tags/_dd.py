from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DescriptionDefinitionElement = NewType("DescriptionDefinitionElement", Element)
"""A `<dd>` element."""


def dd(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> DescriptionDefinitionElement:
    """Provides the description, definition, or value for the preceding term.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dd>
    """
    el = Element("dd")(**attrs, **extra_attrs or {})(*children)
    return DescriptionDefinitionElement(el)
