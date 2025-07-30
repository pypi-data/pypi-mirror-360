from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

LegendElement = NewType("LegendElement", Element)
"""A `<legend>` element."""


def legend(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> LegendElement:
    """Represents a caption for the content of its parent `fieldset`.

    In customizable `select` elements this element is allowed as a child of
    `optgroup`, to provide a label that is easy to target and style. This
    replaces any text set in the `optgroup` element's `label` attribute, and it
    has the same semantics.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/legend>
    """
    el = Element("legend")(**attrs, **extra_attrs or {})(*children)
    return LegendElement(el)
