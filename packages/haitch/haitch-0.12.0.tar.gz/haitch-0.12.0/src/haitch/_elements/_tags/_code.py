from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

CodeElement = NewType("CodeElement", Element)
"""A `<code>` element."""


def code(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> CodeElement:
    """Displays its contents styled as a short fragment of computer code.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/code>
    """
    el = Element("code")(**attrs, **extra_attrs or {})(*children)
    return CodeElement(el)
