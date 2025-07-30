from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

InsElement = NewType("InsElement", Element)
"""An `<ins>` element."""


def ins(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[InsAttrs],
) -> InsElement:
    """Represents a range of text that has been added to a document.

    This can be used when rendering "track changes" or source code diff
    information, for example. The `del` element can be used for the opposite
    purpose.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins>
    """
    el = Element("ins")(**attrs, **extra_attrs or {})(*children)
    return InsElement(el)


class InsAttrs(GlobalAttrs):
    """Attributes for the `<ins>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins#attributes>
    """

    cite: NotRequired[str]
    """A URI for a resource that explains the change.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins#cite>
    """

    datetime: NotRequired[str]
    """Indicates the time and date of the change.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/ins#datetime>
    """
