from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ObjectElement = NewType("ObjectElement", Element)
"""An `<object>` element."""


def object(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ObjectAttrs],
) -> ObjectElement:
    """Defines a group of columns within a table.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object>
    """
    el = Element("object")(**attrs, **extra_attrs or {})(*children)
    return ObjectElement(el)


class ObjectAttrs(GlobalAttrs):
    """Attributes for the `<object>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#attributes>
    """

    data: str
    """The address of the resource as a valid URL.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#data>
    """

    form: NotRequired[str]
    """The form element ID (if any) associated with the object.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#form>
    """

    height: NotRequired[int]
    """The height of the displayed resource in CSS pixels.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#height>
    """

    name: NotRequired[str]
    """A message that the browser can show while loading object.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#name>
    """

    type: str
    """The content type of the resource specified.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#type>
    """

    width: NotRequired[int]
    """The width of the displayed resource in CSS pixels.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/object#width>
    """
