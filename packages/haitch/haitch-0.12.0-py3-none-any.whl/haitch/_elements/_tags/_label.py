from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

LabelElement = NewType("LabelElement", Element)
"""An `<label>` element."""


def label(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[LabelAttrs],
) -> LabelElement:
    """Represents a caption for an item in a user interface.

    To explicitly associate a `<label>` element with an `<input>` element, you
    first need to add the `id` attribute to the `<input>` element. Next, you add
    the `for` attribute to the `<label>` element, where the value of `for` is
    the same as the id in the `<input>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label>
    """
    el = Element("label")(**attrs, **extra_attrs or {})(*children)
    return LabelElement(el)


class LabelAttrs(GlobalAttrs):
    """Attributes for the `<label>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label#attributes>
    """

    for_: NotRequired[str]
    """Single id for a label form-related element in the same document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label#for>
    """
