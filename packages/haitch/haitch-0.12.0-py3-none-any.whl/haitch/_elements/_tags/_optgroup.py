from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

OptgroupElement = NewType("OptgroupElement", Element)
"""An `<optgroup>` element."""


def optgroup(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[OptgroupAttrs],
) -> OptgroupElement:
    """Defines a group of columns within a table.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup>
    """
    el = Element("optgroup")(**attrs, **extra_attrs or {})(*children)
    return OptgroupElement(el)


class OptgroupAttrs(GlobalAttrs):
    """Attributes for the `<optgroup>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup#attributes>
    """

    disabled: NotRequired[bool]
    """Makes the options in the element unselectable.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup#disabled>
    """

    label: str
    """The name of the group options.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup#label>
    """
