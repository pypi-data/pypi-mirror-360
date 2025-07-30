from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SampElement = NewType("SampElement", Element)
"""A `<samp>` element."""


def samp(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SampElement:
    """Encloses inline text representing sample output from a computer program.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/samp>
    """
    el = Element("samp")(**attrs, **extra_attrs or {})(*children)
    return SampElement(el)
