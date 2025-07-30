from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

AddressElement = NewType("AddressElement", Element)
"""An `<address>` element."""


def address(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> AddressElement:
    """Represents contact information for a person or an organization.

    The contact information provided by an `<address>` element's contents can
    take whatever form is appropriate for the context, and may include any type
    of contact information that is needed, such as a physical address, URL,
    email address, phone number, social media handle, geographic coordinates,
    and so forth. The `<address>` element should include the name of the person,
    people, or organization to which the contact information refers.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/address>
    """
    el = Element("address")(**attrs, **extra_attrs or {})(*children)
    return AddressElement(el)
