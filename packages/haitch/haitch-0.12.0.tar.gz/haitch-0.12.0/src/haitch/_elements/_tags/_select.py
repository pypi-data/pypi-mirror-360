from __future__ import annotations

from typing import Literal, NewType, Optional, Union

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SelectElement = NewType("SelectElement", Element)
"""A `<select>` element."""


def select(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[SelectAttrs],
) -> SelectElement:
    """Represents a control that provides a menu of options.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select>
    """
    el = Element("select")(**attrs, **extra_attrs or {})(*children)
    return SelectElement(el)


class SelectAttrs(GlobalAttrs):
    """Attributes for the `<select>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#attributes>
    """

    autocomplete: NotRequired[Union[Literal["on", "off"], str]]
    """Controls whether entered text can be automatically completed.

      - `off`: user must explicitly enter a value for every use.
      - `on`: the browser can autocomplete previous entries.
      - `<token-list>`: space separated autofill detail tokens.

    Note: when not specified, this attribute inherits from form owner.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#autocomplete>
    """

    disabled: NotRequired[bool]
    """Whether the user can interact with the control.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#disabled>
    """

    form: NotRequired[str]
    """A form ID to associate the output its form owner.

    This allows you to place the element anywhere in the document, not just
    inside a `form` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#form>
    """

    multiple: NotRequired[bool]
    """Whether multiple options can be selected in the list.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#multiple>
    """

    name: NotRequired[str]
    """Specifies the name of the control.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#name>
    """

    required: NotRequired[bool]
    """Specifies that an option with a non-empty string must be selected.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#required>
    """

    size: NotRequired[int]
    """Specifies the the number of rows that should in a scrolling list.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select#size>
    """
