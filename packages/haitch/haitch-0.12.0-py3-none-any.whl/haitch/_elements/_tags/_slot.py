from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SlotElement = NewType("SlotElement", Element)
"""A `<slot>` element."""


def slot(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[SlotAttrs],
) -> SlotElement:
    """Defines a group of columns within a table.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/slot>
    """
    el = Element("slot")(**attrs, **extra_attrs or {})(*children)
    return SlotElement(el)


class SlotAttrs(GlobalAttrs):
    """Attributes for the `<slot>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/slot#attributes>
    """

    name: NotRequired[str]
    """The slot's name.

    When the slot's containing component gets rendered, the slot is rendered
    with the custom element's child that has a matching global `slot` attribute.
    Unnamed slots have the name default to the empty string. Names should be
    unique per shadow root: if you have two slots with the same name, all of the
    elements with a matching `slot` attribute will be assigned to the first slot
    with that name.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/slot#name>
    """
