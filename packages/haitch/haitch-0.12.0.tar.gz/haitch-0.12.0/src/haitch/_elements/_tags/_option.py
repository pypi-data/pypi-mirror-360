from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

OptionElement = NewType("OptionElement", Element)
"""An `<option>` element."""


def option(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[OptionAttrs],
) -> OptionElement:
    """Used to define an item contained element that provides options.

    Such elements include: `select`, `optgroup` and `datalist`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option>
    """
    el = Element("option")(**attrs, **extra_attrs or {})(*children)
    return OptionElement(el)


class OptionAttrs(GlobalAttrs):
    """Attributes for the `<option>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option#attributes>
    """

    disabled: NotRequired[bool]
    """If set, the option is not checkable.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option#disabled>
    """

    label: NotRequired[str]
    """Text that indicates the meaning of the option.

    Note: the `value` attribute will be set as the label if undefined.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option#label>
    """

    selected: NotRequired[bool]
    """Intializes the option as already selected.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option#selected>
    """

    value: NotRequired[str]
    """The content to be submited with the form when selected.

    Note: if omitted, the value is taken from the text content of the element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/option#value>
    """
