from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

AnchorElement = NewType("AnchorElement", Element)
"""An `<a>` element."""


def a(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[AnchorAttrs],
) -> AnchorElement:
    """Creates a hyperlink with its `href` attribute.

    A hyperlink can link to web pages, files, email addresses, locations in the
    same page, or anything else a URL can address.

    Content within each <a> should indicate the link's destination. If the href
    attribute is present, pressing the enter key while focused on the <a>
    element will activate it.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a>
    """
    el = Element("a")(**attrs, **extra_attrs or {})(*children)
    return AnchorElement(el)


class AnchorAttrs(GlobalAttrs):
    """Attributes for the `<a>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#attributes>
    """

    download: NotRequired[str]
    """Causes the browser to treat the linked URL as a download.

    Note: `download` only works for same-origin URLs, or the `blob:` and `data:`
    schemes.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#download>
    """

    href: NotRequired[str]
    """The URL that the hyperlink points to.

    Links are not restricted to HTTP-based URLs - they can use any URL scheme
    supported by browsers:
        - Sections of a page with document fragments
        - Specific text portions with text fragments
        - Pieces of media files with media fragments
        - Telephone numbers with `tel:` URLs
        - Email addresses with `mailto:` URLs
        - SMS text messages with `sms:` URLs

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#href>
    """

    hreflang: NotRequired[str]
    """Hints at the human language (code) of the linked URL.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#hreflang>
    """

    ping: NotRequired[str]
    """A space-separated list of URLs to ping when link is followed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#ping>
    """

    referrerpolicy: NotRequired[
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
    ]
    """How much of the referrer to send when following the link.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#referrerpolicy>
    """

    rel: NotRequired[str]
    """The relationship of the linked URL as space-separated link types.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#rel>
    """

    target: NotRequired[str]
    """Where to display the linked URL.

    The following keywords have special meaning: `_self`, `_blank`, `_parent`,
    `_top`.

    Note: setting `target="_blank"` on `<a>` elements implicitly provides the
    same `rel` behavior as setting `rel="noopener"` which does not set
    `window.opener`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#rel>
    """

    type_: NotRequired[str]
    """Hints at the linked URL's format with a MIME type.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#type>
    """
