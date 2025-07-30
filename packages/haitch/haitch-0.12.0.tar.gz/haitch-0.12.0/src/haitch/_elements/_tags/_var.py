from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

VarElement = NewType("VarElement", Element)
"""A `<var>` element."""


def var(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> VarElement:
    """Represents the name of a variable.

    This is often used in a mathematical expression or a programming context.
    It's typically presented using an italicized version of the current
    typeface, although the behavior is browser-dependent.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/var>
    """
    el = Element("var")(**attrs, **extra_attrs or {})(*children)
    return VarElement(el)
