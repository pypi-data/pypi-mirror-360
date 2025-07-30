from __future__ import annotations

from typing import Literal, NewType, Optional, Union

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TextareaElement = NewType("TextareaElement", Element)
"""A `<textarea>` element."""


def textarea(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[TextareaAttrs],
) -> TextareaElement:
    """Represents a multi-line plain-text editing control.

    This is useful when you want to allow users to enter a sizeable amount of
    free-form text, for example a comment on a review or feedback form.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea>
    """
    el = Element("textarea")(**attrs, **extra_attrs or {})(*children)
    return TextareaElement(el)


class TextareaAttrs(GlobalAttrs):
    """Attributes for the `<textarea>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#attributes>
    """

    autocomplete: NotRequired[Union[Literal["on", "off"], str]]
    """Controls whether entered text can be automatically completed.

      - `off`: user must explicitly enter a value for every use.
      - `on`: the browser can autocomplete previous entries.
      - `<token-list>`: space separated autofill detail tokens.

    Note: when not specified, this attribute inherits from form owner.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#autocomplete>
    """

    autocorrect: NotRequired[Literal["on", "off"]]
    """Activate automatic spelling correction and processing of text.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#autocorrect>
    """

    cols: NotRequired[int]
    """Visible width of the text control in average character width.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#cols>
    """

    dirname: NotRequired[Literal["ltr", "rtl"]]
    """Indicates the text directionality.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#dirname>
    """

    disabled: NotRequired[bool]
    """Whether the user can interact with the control.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#disabled>
    """

    form: NotRequired[str]
    """A form ID to associate the output its form owner.

    This allows you to place the element anywhere in the document, not just
    inside a `form` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#form>
    """

    maxlength: NotRequired[int]
    """Maximum string length that a user can enter.

    Length is measured by UTF-16 code units. If not specified, the user can
    enter an unlimited number of characters.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#maxlength>
    """

    minlength: NotRequired[int]
    """Minimum string length that a user must enter.

    Length is measured by UTF-16 code units.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#minlength>
    """

    name: NotRequired[str]
    """The name of the control.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#name>
    """

    placeholder: NotRequired[str]
    """A hint to the user of what can be entered in the control.

    Note: carriage return or line-feeds within the placeholder text must be
    treated as line breaks when rendering the hint.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#placeholder>
    """

    readonly: NotRequired[bool]
    """Prevent user from modifying the value of the control.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#readonly>
    """

    required: NotRequired[bool]
    """Specifies that the user must fill in a value before submitting a form.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#required>
    """

    rows: NotRequired[int]
    """Number of visible text lines for the control (default: 2).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#rows>
    """

    wrap: NotRequired[Literal["hard", "soft"]]
    """Indicates how the control should wrap the value for form submission.

      - `hard`: automatically insert line breaks when width reached. The `col`
        attribute must be specified for this to take effect.
      - `soft`: ensure all line breaks in the entered value are a `CR+LF` pair,
        but no additional line breaks are added to the value. This is the
        default option.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea#wrap>
    """
