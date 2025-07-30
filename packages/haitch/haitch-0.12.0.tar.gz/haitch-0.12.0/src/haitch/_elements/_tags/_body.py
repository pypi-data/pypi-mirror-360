from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

BodyElement = NewType("BodyElement", Element)
"""A `<body>` element."""


def body(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[BodyAttrs],
) -> BodyElement:
    """Represents the content of an HTML document.

    Note: there can only be one `<body>` element in a document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body>
    """
    el = Element("body")(**attrs, **extra_attrs or {})(*children)
    return BodyElement(el)


class BodyAttrs(GlobalAttrs):
    """Attributes for the `<body>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#attributes>
    """

    onafterprint: NotRequired[str]
    """Function to call after the user has printed the document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onafterprint>
    """

    onbeforeprint: NotRequired[str]
    """Function to call when the user requests printing of the document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onbeforeprint>
    """

    onbeforeunload: NotRequired[str]
    """Function to call when the document is about to be unloaded.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onbeforeunload>
    """

    onblur: NotRequired[str]
    """Function to call when the document loses focus.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onblur>
    """

    onerror: NotRequired[str]
    """Function to call when the document fails to load properly.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onerror>
    """

    onfocus: NotRequired[str]
    """Function to call when the document receives focus.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onfocus>
    """

    onhashchange: NotRequired[str]
    """Function to call when the fragment id part of the document's current address changed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onhashchange>
    """

    onlanguagechange: NotRequired[str]
    """Function to call when the preferred language changed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onlanguagechange>
    """

    onload: NotRequired[str]
    """Function to call when the document has finished loading.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onload>
    """

    onmessage: NotRequired[str]
    """Function to call when the document has received a message.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onmessage>
    """

    onoffline: NotRequired[str]
    """Function to call when network communication has failed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onoffline>
    """

    ononline: NotRequired[str]
    """Function to call when network communication has been restored.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#ononline>
    """

    onpopstate: NotRequired[str]
    """Function to call when the user has navigated session history.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onpopstate>
    """

    onredo: NotRequired[str]
    """Function to call when user moves forward in undo transaction history.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onredo>
    """

    onresize: NotRequired[str]
    """Function to call when the document has been resized.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onresize>
    """

    onstorage: NotRequired[str]
    """Function to call when the storage area has changed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onstorage>
    """

    onundo: NotRequired[str]
    """Function to call when user moves backward in undo transaction history.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onundo>
    """

    onunload: NotRequired[str]
    """Function to call when the document is going away.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/body#onunload>
    """
