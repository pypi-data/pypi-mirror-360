from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

UElement = NewType("UElement", Element)
"""A `<u>` element."""


def u(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> UElement:
    """Indicates that content has non-textual annotation.

    This is rendered by default as a single solid underline, but may be altered
    using CSS. A common use case is to annotate spelling errors.

    Warning: this element used to be called the "underline" element in older
    versions of HTML, and is still sometimes misused in this way. To underline
    text, you should instead apply a style that includes the `text-decoration`
    property set to `underline`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/u>
    """
    el = Element("u")(**attrs, **extra_attrs or {})(*children)
    return UElement(el)
