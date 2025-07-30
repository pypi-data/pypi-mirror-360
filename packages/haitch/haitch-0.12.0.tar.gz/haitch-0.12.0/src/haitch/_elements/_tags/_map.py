from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

MapElement = NewType("MapElement", Element)
"""A `<map>` element."""


def map(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[MapAttrs],
) -> MapElement:
    """Defines an image map (a clickable link area).

    Used with the `area` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/map>
    """
    el = Element("map")(**attrs, **extra_attrs or {})(*children)
    return MapElement(el)


class MapAttrs(GlobalAttrs):
    """Attributes for the `<map>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/map#attributes>
    """

    name: str
    """Gives the map a name so that it can be referenced.

    The attribute must be present and must have a non-empty value with no space
    characters. The value must not be equal to the value of the `name` attribute
    of another map element in the same document.

    Note: if an `id` attribute is set, it must match the `name` attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/map#name>
    """
