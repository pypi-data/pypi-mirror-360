from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

FieldsetElement = NewType("FieldsetElement", Element)
"""A `<fieldset>` element."""


def fieldset(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[FieldsetAttrs],
) -> FieldsetElement:
    """Defines a group of columns within a table.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset>
    """
    el = Element("fieldset")(**attrs, **extra_attrs or {})(*children)
    return FieldsetElement(el)


class FieldsetAttrs(GlobalAttrs):
    """Attributes for the `<fieldset>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset#attributes>
    """

    disabled: NotRequired[bool]
    """Disables all form controls that are descendants.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset#disabled>
    """

    form: NotRequired[str]
    """Expects an `id` attribute value from a form.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset#form>
    """

    name: NotRequired[str]
    """The name associated with the group.

    Note: the caption for the fieldset is given by the first `legend` element
    nested inside it.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/fieldset#name>
    """
