from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

NoscriptElement = NewType("NoscriptElement", Element)
"""A `<noscript>` element."""


def noscript(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> NoscriptElement:
    """Defines HTML to be inserted if a script type on the page is unsupported.

    This can occur if scripting (JavaScript) is turned off in the browser.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/noscript>
    """
    el = Element("noscript")(**attrs, **extra_attrs or {})(*children)
    return NoscriptElement(el)
