from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DataElement = NewType("DataElement", Element)
"""A `<data>` element."""


def data(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[DataAttrs],
) -> DataElement:
    """Links a given piece of content with a machine-readable translation.

    If the content is time- or date-related, `time` element must be used.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data>
    """
    el = Element("data")(**attrs, **extra_attrs or {})(*children)
    return DataElement(el)


class DataAttrs(GlobalAttrs):
    """Attributes for the `<data>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data#attributes>
    """

    value: NotRequired[str]
    """Specifies the machine-readable translation of the content.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/data#value>
    """
