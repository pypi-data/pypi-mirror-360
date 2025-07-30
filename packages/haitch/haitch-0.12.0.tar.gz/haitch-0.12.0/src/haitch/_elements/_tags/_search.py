from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SearchElement = NewType("SearchElement", Element)
"""A `<search>` element."""


def search(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SearchElement:
    """Represents content related to performing search or filtering.

    The `<search>` element semantically identifies the purpose of the element's
    contents as having search or filtering capabilities. The search or filtering
    functionality can be for the website or application, the current web page or
    document, or the entire Internet or subsection thereof.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/search>
    """
    el = Element("search")(**attrs, **extra_attrs or {})(*children)
    return SearchElement(el)
