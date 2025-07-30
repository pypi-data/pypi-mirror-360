from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

MeterElement = NewType("MeterElement", Element)
"""A `<meter>` element."""


def meter(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[MeterAttrs],
) -> MeterElement:
    """Represents either a scalar within a range or fractional value.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter>
    """
    el = Element("meter")(**attrs, **extra_attrs or {})(*children)
    return MeterElement(el)


class MeterAttrs(GlobalAttrs):
    """Attributes for the `<meter>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#attributes>
    """

    value: str
    """Current numeric value.

    This must be between the minimum and maximum values.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#value>
    """

    min: NotRequired[str]
    """The lower numeric bound of the measured range (default: 0).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#min>
    """

    max: NotRequired[str]
    """The upper numeric bound of the measured range (default: 1).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#max>
    """

    low: NotRequired[str]
    """The upper numeric bound of the low end of the measured range.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#low>
    """

    high: NotRequired[str]
    """The lower numeric bound of the high end of the measured range.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#high>
    """

    optimum: NotRequired[str]
    """The optimal numeric value.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#optimum>
    """

    form: NotRequired[str]
    """Explicitly set a `form` owner for the meter element.

    If omitted, the element is associated with the ancestor `form` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter#form>
    """
