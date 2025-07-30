from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DelElement = NewType("DelElement", Element)
"""A `<del>` element."""


def del_(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[DelAttrs],
) -> DelElement:
    """Represents a range of text that has been deleted from a document.

    This can be used when rendering "track changes" or source code diff
    information, for example. The `ins` element can be used for the opposite
    purpose.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del>
    """
    el = Element("del")(**attrs, **extra_attrs or {})(*children)
    return DelElement(el)


class DelAttrs(GlobalAttrs):
    """Attributes for the `<del>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del#attributes>
    """

    cite: NotRequired[str]
    """A URI for a resource that explains the change.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del#cite>
    """

    datetime: NotRequired[str]
    """Indicates the time and date of the change.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del#datetime>
    """
