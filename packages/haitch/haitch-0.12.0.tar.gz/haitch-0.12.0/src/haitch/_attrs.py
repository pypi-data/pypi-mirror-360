import html
from typing import Literal, Mapping, TypedDict, Union

from typing_extensions import NotRequired

AttributeValue = Union[str, bool, int]
"""An acceptable value type to be passed to an attribute."""

Attributes = Mapping[str, AttributeValue]
"""Mapping of element attributes."""


def serialize_attribute(key: str, value: AttributeValue) -> str:
    """Convert a key value pair into a valid HTML attribute."""
    key_ = key.rstrip("_").replace("_", "-")

    if isinstance(value, bool):
        return f" {key_}" if value else ""

    if isinstance(value, int):
        value = str(value)

    if isinstance(value, str):
        return f' {key_}="{html.escape(value)}"'

    raise ValueError(
        f"Attribute value must be `str`, `int`, or `bool`, not {type(value)}"
    )


class GlobalAttrs(TypedDict):
    """Global attributes for elements.

    These are attributes common to all HTML elements; they can be used on
    all elements, though they may have no effect on some elements.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes>
    """

    accesskey: NotRequired[str]
    """Provides a hint for generating a keyboard shortcut.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/accesskey>
    """

    autocapitalize: NotRequired[Literal["off", "on", "words", "characters"]]
    """Controls whether inputted text is automatically capitalized.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/autocapitalize>
    """

    autofocus: NotRequired[bool]
    """Indicates that an element is to be focused on page load.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/autofocus>
    """

    class_: NotRequired[str]
    """A space-separated list of the classes of the element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/class>
    """

    dir: NotRequired[Literal["ltr", "rtl", "auto"]]
    """Indicates the directionality of the element's text.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/dir>
    """

    draggable: NotRequired[Literal["true", "false"]]
    """Indicates whether the element can be dragged.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/draggable>
    """

    enterkeyhint: NotRequired[
        Literal["enter", "done", "go", "next", "previous", "search", "send"]
    ]
    """Defines what action label to present for the enter key on virtual keyboards.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/enterkeyhint>
    """

    exportparts: NotRequired[str]
    """Select and style elements existing in nested shadow trees, by exporting their
    part names.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/exportparts>
    """

    hidden: NotRequired[Literal["", "hidden", "until-found"]]
    """Indicates that the content of an element should not be presented to the user.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/hidden>
    """

    id_: NotRequired[str]
    """Defines a unique identifier which must be unique in the whole document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/id>
    """

    inert: NotRequired[bool]
    """Makes the browser disregard user input events for the element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/inert>
    """

    inputmode: NotRequired[bool]
    """Provides a hint to the browser about the type of virtual keyboard configuration.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/inputmode>
    """

    is_: NotRequired[str]
    """Allows you to specify that an element should behave like a registered custom element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/is>
    """

    itemid: NotRequired[str]
    """The unique, global identifier of an item.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/itemid>
    """

    itemprop: NotRequired[str]
    """Used to add properties to an item.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/itemprop>
    """

    itemref: NotRequired[str]
    """Provide a list of element ids with additional properties elsewhere in the document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/itemref>
    """

    itemscope: NotRequired[bool]
    """Defines the scope of associated metadata.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/itemscope>
    """

    itemtype: NotRequired[str]
    """Specifies the URL of the vocabulary that will be used to define itemprops in the data.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/itemtype>
    """

    lang: NotRequired[str]
    """Helps define the language of an element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/lang>
    """

    nonce: NotRequired[str]
    """A cryptographic nonce ("number used once") used by Content Security Policy.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/nonce>
    """

    part: NotRequired[str]
    """A space-separated list of the part names of the element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/part>
    """

    popover: NotRequired[bool]
    """Used to designate an element as a popover element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/popover>
    """

    role: NotRequired[str]
    """Defines the semantic meaning of the content (accessibility).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/role>
    """

    slot: NotRequired[str]
    """Assigns a slot in a shadow DOM shadow tree to an element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/slot>
    """

    spellcheck: NotRequired[Literal["", "true", "false"]]
    """An enumerated attribute defines whether the element may be checked for spelling errors.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/spellcheck>
    """

    style: NotRequired[str]
    """Contains CSS styling declarations to be applied to element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/style>
    """

    tabindex: NotRequired[int]
    """An integer attribute indicating if the element can take input focus.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/tabindex>
    """

    title: NotRequired[str]
    """Contains a text representing advisory information related to the element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title>
    """

    translate: NotRequired[Literal["", "yes", "no"]]
    """An enumerated attribute for translation purposes.

    The attribute is used to specify whether an element's attribute values and the
    values of its Text node children are to be translated when the page is localized
    or whether to leave them unchanged.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/translate>
    """

    virtualkeyboardpolicy: NotRequired[Literal["", "auto", "manual"]]
    """An enumerated attribute used to control the on-screen virtual keyboard behaviour.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/virtualkeyboardpolicy>
    """
