from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

ColElement = NewType("ColElement", VoidElement)
"""A `<col>` element."""


def col(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ColAttrs],
) -> ColElement:
    """Defines one or more columns in a column group.

    Note: The `<col>` element is only valid as a child of a `<colgroup>` element
    that has no span attribute defined.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/col>
    """
    el = VoidElement("col")(**attrs, **extra_attrs or {})
    return ColElement(el)


class ColAttrs(GlobalAttrs):
    """Attributes for the `<col>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/col#attributes>
    """

    span: NotRequired[int]
    """Specifies the number of consecutive columns the <col> element spans.

    Warning: the value must be a positive integer greater than zero. If not
    present, its default value is 1.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/col#span>
    """
