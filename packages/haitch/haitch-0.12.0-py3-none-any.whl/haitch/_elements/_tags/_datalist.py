from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DatalistElement = NewType("DatalistElement", Element)
"""A `<datalist>` element."""


def datalist(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> DatalistElement:
    """Contains a set of `option` elements.

    The list represents the permissible or recommended options available to
    choose from within other controls. To bind the `datalist` elements to the
    control, you need to give it a unique identifier in `id` attribute.

    Note: a `datalist` element is only a list of suggested values for an
    associated control. The control can still accept any value that passes
    validation.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/datalist>
    """
    el = Element("datalist")(**attrs, **extra_attrs or {})(*children)
    return DatalistElement(el)
