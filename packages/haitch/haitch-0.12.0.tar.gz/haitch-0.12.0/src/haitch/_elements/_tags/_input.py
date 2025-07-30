from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

InputElement = NewType("InputElement", VoidElement)
"""An `<input>` element."""


def input(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[InputAttrs],
) -> InputElement:
    """Creates interactive controls for web-based forms.

    The primary purpose of this element is to accept data from user. A wide
    variety of types of input data and control widgets are available, depending
    on the device and user agent.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input>
    """
    el = VoidElement("input")(**attrs, **extra_attrs or {})
    return InputElement(el)


class InputAttrs(GlobalAttrs):
    """Attributes for the `<input>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#attributes>
    """

    name: NotRequired[str]
    """Name of the form control.

    This value is only required when submitting a form.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#name>
    """

    type_: NotRequired[
        Literal[
            "button",
            "checkbox",
            "color",
            "date",
            "datetime-local",
            "email",
            "file",
            "hidden",
            "image",
            "month",
            "number",
            "password",
            "radio",
            "range",
            "reset",
            "search",
            "submit",
            "tel",
            "text",
            "time",
            "url",
            "week",
        ]
    ]
    """The type of input data to receive from the user.

    Defaults to "text" when value not provided.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types>
    """

    accept: NotRequired[str]
    """Defines which file types are selectable in a file upload control.

    Valid types: `file`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#accept>
    """

    alt: NotRequired[str]
    """Alternate text for image type (accessibility).

    Valid types: `image`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#alt>
    """

    autocomplete: NotRequired[str]
    """Hint for form autofill feature (space-separated string).

    Valid types: all except `checkbox`, `radio` and buttons

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#autocomplete>
    """

    capture: NotRequired[bool]
    """Media capture input method in file upload controls.

    Valid types: `file`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#capture>
    """

    checked: NotRequired[bool]
    """Whether the command or control is checked.

    Note: Unlike other input controls, a checkboxes and radio buttons value are
    only included in the submitted data if they are currently checked. If they
    are, the name and the value(s) of the checked controls are submitted.

    For example, if a checkbox whose name is fruit has a value of cherry, and
    the checkbox is checked, the form data submitted will include fruit=cherry.
    If the checkbox isn't active, it isn't listed in the form data at all. The
    default value for checkboxes and radio buttons is on.

    Valid types: `checkbox`, `radio`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#checked>
    """

    dirname: NotRequired[str]
    """Name of form field for sending the element's directionality.

    Valid types: `hidden`, `text`, `search`, `url`, `tel`, `email`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#dirname>
    """

    disabled: NotRequired[bool]
    """Whether the form control is disabled.

    Note: Although not required by the specification, Firefox will by default
    persist the dynamic disabled state of an `<input>` across page loads. Use
    the autocomplete attribute to control this feature.

    Valid types: all

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#disabled>
    """

    form: NotRequired[str]
    """Associates the control with a form element.

    Note: An input can only be associated with one form.

    Valid types: all

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#form>
    """

    formaction: NotRequired[str]
    """URL to use for form submission.

    Valid types: `image`, `submit`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formaction>
    """

    formenctype: NotRequired[
        Literal[
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
    ]
    """Form data set encoding type to use for form submission.

    Valid types: `image`, `submit`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formenctype>
    """

    formmethod: NotRequired[Literal["get", "post", "dialog"]]
    """HTTP submission method to use for form submission.

    Valid types: `image`, `submit`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formmethod>
    """

    formnovalidate: NotRequired[bool]
    """Bypass form control validation for form submission.

    Valid types: `image`, `submit`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formnovalidate>
    """

    formtarget: NotRequired[str]
    """Browsing context for form submission.

    Note: In addition to the actual names of tabs, windows, or inline frames

    There are a few special keywords that can be used:

      - `_self` (default): load into same browsing content as current one.
      - `_blank`: load into a new unamed browsing context.
      - `_parent`: load into the parent browsing context.
      - `_top`: load into the top-level browsing context.

    Valid types: `image`, `submit`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#formtarget>
    """

    height: NotRequired[int]
    """Same as height attribute for `<img>`; vertical dimension.

    Valid types: `image`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#height>
    """

    list_: NotRequired[str]
    """Value of the id attribute of the `<datalist>` of autocomplete options.

    Valid types: all except `hidden`, `password`, `checkbox`, `radio` and
    buttons

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#list>
    """

    max: NotRequired[int]
    """Maximum input value.

    Note: If the value isn't a number, then the element has no maximum value.

    Valid types: `date`, `month`, `week`, `time`, `datetime-local`, `number`,
    `range`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#max>
    """

    maxlength: NotRequired[int]
    """Maximum length (number of characters) of value.

    Valid types: `text`, `search`, `url`, `tel`, `email`, `password`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#maxlength>
    """

    min: NotRequired[int]
    """Minimum input value.

    Note: If the value isn't a number, then the element has no minimum value.

    Valid types: `date`, `month`, `week`, `time`, `datetime-local`, `number`,
    `range`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#min>
    """

    minlength: NotRequired[int]
    """Minimum length (number of characters) of value.

    Valid types: `text`, `search`, `url`, `tel`, `email`, `password`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#minlength>
    """

    multiple: NotRequired[bool]
    """User can enter multiple values.

    For example, a user can input a comma separated email addresses in the email
    widget or more than one file with the file input.

    Valid types: `email`, `file`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#multiple>
    """

    pattern: NotRequired[str]
    """The pattern attribute defines a regex that the input value must match.

    Valid types: `text`, `search`, `url`, `tel`, `email` and `password`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#pattern>
    """

    placeholder: NotRequired[str]
    """Hint to the user as to what kind of info is expected in the field.

    Note: The placeholder attribute is not as semantically useful as other ways
    to explain your form, and can cause unexpected technical issues with your
    content.

    Valid types: `text`, `search`, `url`, `tel`, `email`, `password` and
    `number`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#placeholder>
    """

    popovertarget: NotRequired[Literal["hide", "show", "toggle"]]
    """Turns an `<input type="button">` element into a popover control button.

    Valid types: `button`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#popovertarget>
    """

    readonly: NotRequired[bool]
    """Indicates that user should not be able to edit the value of the input.

    Valid types: all except `hidden`, `range`, `color`, `checkbox`, `radio` and
    buttons

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#readonly>
    """

    required: NotRequired[bool]
    """A value is required or must be checked for the form to be submittable.

    Valid types: all except `hidden`, `range`, `color` and buttons

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#required>
    """

    size: NotRequired[str]
    """Specifies how much of the input is shown.

    Note: CSS `width` takes precedence over the `size` attribute.

    Valid types: `email`, `password`, `tel`, `url`, and `text`, the `size`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#size>
    """

    src: NotRequired[str]
    """URL of the image file to display.

    This is also used to represent a graphical submit button.

    Valid types: `image`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#src>
    """

    step: NotRequired[int]
    """A number that specifies the granularity that the value must adhere to.

    Note: Note: When the data entered by the user doesn't adhere to the stepping
    configuration, the value is considered invalid in constraint validation and
    will match the :invalid pseudoclass.

    Valid types: `date`, `month`, `week`, `time`, `datetime-local`, `number` and
    `range`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#step>
    """

    value: NotRequired[str]
    """The input control's value.

    Note: The value attribute is always optional, though should be considered
    mandatory for `checkbox`, `radio`, and `hidden`.

    Valid types: `button`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#value>
    """

    width: NotRequired[int]
    """Same as width attribute for `<img>`; horizontal dimension.

    Valid types: `image`

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#width>
    """
