from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DetailsElement = NewType("DetailsElement", Element)
"""A `<details>` element."""


def details(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[DetailsAttrs],
) -> DetailsElement:
    """Creates a disclosure widget that opens and closes.

    A summary or label must be provided using the `<summary>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details>
    """
    el = Element("details")(**attrs, **extra_attrs or {})(*children)
    return DetailsElement(el)


class DetailsAttrs(GlobalAttrs):
    """Attributes for the `<details>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details#attributes>
    """

    open: NotRequired[bool]
    """Indicates whether the details are currently visible.

    By default, this attribute is absent which means the details are not
    visible.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details#open>
    """

    name: NotRequired[str]
    """Enables multiple <details> elements to be connected.

    This allows developers to easily create UI features such as accordions
    without scripting, allowing only one open at a time.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details#name>
    """
