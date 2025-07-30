from __future__ import annotations

from typing import Literal, NewType, Optional, Union

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ButtonElement = NewType("ButtonElement", Element)
"""A `<button>` element."""


def button(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ButtonAttrs],
) -> ButtonElement:
    """An interactive element activated by a user.

    A button can be activated with a mouse, keyboard, finger, voice command,
    or other assistive technology. Once activated, it then performs an action,
    such as submitting a `form` or opening a dialog.

    By default, HTML buttons are presented in a style resembling the platform
    the user agent runs on, but you can change buttons' appearance with CSS.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button>
    """
    el = Element("button")(**attrs, **extra_attrs or {})(*children)
    return ButtonElement(el)


class ButtonAttrs(GlobalAttrs):
    """Attributes for the `<button>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#attributes>
    """

    command: NotRequired[
        Union[
            Literal[
                "show-modal",
                "close",
                "request-close",
                "show-popover",
                "hide-popover",
                "toggle-popover",
            ],
            str,
        ]
    ]
    """Specifies the action to be performed on an element being controlled.

      - `show-modal`: shows a dialog as modal.
      - `close`: button closes a dialog element.
      - `request-close`: requests to close a dialog element.
      - `show-popover`: shows a hidden popover.
      - `hide-popover`: hides a showing popover.
      - `toggle-popover`: toggles a popover between show and hidden.
      - `--`: custom values prefixed with the two hyphen characters.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#command>
    """

    commandfor: NotRequired[str]
    """Turns a button element into a command element.

    Takes the ID of the element to control as its value.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#commandfor>
    """

    disabled: NotRequired[bool]
    """Prevents the user from interacting with the button.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#disabled>
    """

    form: NotRequired[str]
    """Associates the button with its form owner.

    Takes the ID of the form element in the same document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button#form>
    """

    formenctype: NotRequired[
        Literal[
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
    ]
    """Form data set encoding type to use for form submission.

      - `application/x-www-form-urlencoded`: default attribute is not used.
      - `multipart/form-data`: submits `input` elements with their type
        attributes set `file`.
      - `text/plain`: debugging aid that shouldn't be used in production.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formenctype>
    """

    formmethod: NotRequired[Literal["post", "get", "dialog"]]
    """Form data set encoding type to use for form submission.

      - `post`: form data are included in the body of HTTP request.
      - `get`: form data are appended to the form's action URL with a `?`.
      - `dialog`: indicates that hte button closes the `dialog` with which it is
        associated, and does not transmit the form data at all.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formmethod>
    """

    formnovalidate: NotRequired[bool]
    """Specifies that the form is not to be validated when submitted.

    Note: button must be a submit button.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formnovalidate>
    """

    formtarget: NotRequired[Literal["_self", "_blank", "_parent", "_top"]]
    """Indicates where to display the response from submitting a form.

      - `_self`: load response into same browsing context as current.
      - `_blank`: load response into a new unnamed context.
      - `_parent`: load response into the parent browsing context.
      - `_top`: load response into the top-level browsing context.

    Note: button must be a submit button.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formtarget>
    """

    name: NotRequired[str]
    """The name of the button submitted as a pair with the button's `value`.

    Note: the name/value pair will be part of the form data submitted.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#name>
    """

    popovertarget: NotRequired[str]
    """Turns a button into a popover control button.

    This attribute takes the ID of the popover element to control as its value.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#popovertarget>
    """

    popovertargetaction: NotRequired[Literal["hide", "show", "toggle"]]
    """Specifies the action to be performed on a popover element.

      - `hide`: hides the shown popover.
      - `show`: shows a hidden popover.
      - `toggle`: toggles a popover between show and hidden.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#popovertargetaction>
    """

    value: NotRequired[str]
    """The value associated with the button `name`.

    Note: the name/value pair will be part of the form data submitted.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value>
    """
