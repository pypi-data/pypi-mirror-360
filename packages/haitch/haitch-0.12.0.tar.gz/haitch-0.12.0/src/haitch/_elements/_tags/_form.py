from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

FormElement = NewType("FormElement", Element)
"""An `<form>` element."""


def form(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[FormAttrs],
) -> FormElement:
    """Represents a section containing controls for submitting information.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form>
    """
    el = Element("form")(**attrs, **extra_attrs or {})(*children)
    return FormElement(el)


class FormAttrs(GlobalAttrs):
    """Attributes for the `<form>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#attributes>
    """

    accept_charset: NotRequired[str]
    """Space-separated character encodings the server accepts.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#accept-charset>
    """

    action: NotRequired[str]
    """The URL that processes the form submission.

    This value can be overridden by a `formaction` attribute on a `<button>`,
    `<input type="submit">`, or `<input type="image">` element. This attribute
    is ignored when `method="dialog"` is set.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#action>
    """

    enctype: NotRequired[
        Literal[
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
        ]
    ]
    """The encoding type.

    If the value of the method attribute is post, enctype is the MIME type of
    the form submission.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#enctype>
    """

    method: NotRequired[Literal["post", "get", "dialog"]]
    """The HTTP method to submit the form with.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#method>
    """

    name: NotRequired[str]
    """The name of the form.

    The value must not be the empty string, and must be unique among the `form`
    elements in the forms collection that it is in, if any.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#name>
    """

    novalidate: NotRequired[bool]
    """Indicates that the form shouldn't be validated when submitted.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#novalidate>
    """

    rel: NotRequired[str]
    """Controls the annotations and what kinds of links the form creates.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#rel>
    """

    target: NotRequired[str]
    """A keyword of the browsing context to display the linked resource.

    The following keywords have special meaning:

      - `_self` (default): load into same browsing content as current one.
      - `_blank`: load into a new unamed browsing context.
      - `_parent`: load into the parent browsing context.
      - `_top`: load into the top-level browsing context.
      - `_unfencedTop`: load the response from a form inside an embedded fenced
        frame into the top-levl frame (only available inside fenced frames).

    Note: this value can be override by a `formtarget attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form#target>
    """
