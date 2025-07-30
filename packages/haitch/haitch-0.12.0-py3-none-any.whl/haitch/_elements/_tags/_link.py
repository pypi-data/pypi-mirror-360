from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

LinkElement = NewType("LinkElement", VoidElement)
"""A `<link>` element."""


def link(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[LinkAttrs],
) -> LinkElement:
    """Specifies relationships between current document and external resource.

    This element is most commonly used to link to stylesheets, but is also used
    to establish site icons (both "favicon" style icons and icons for the home
    screen and apps on mobile devices) among other things.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link>
    """
    el = VoidElement("link")(**attrs, **extra_attrs or {})
    return LinkElement(el)


class LinkAttrs(GlobalAttrs):
    """Attributes for the `<link>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#attributes>
    """

    href: str
    """Specifies the URL of the linked resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#href>
    """

    rel: str
    """Relationship between a linked resource and the current document.

    Valid values: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel>

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#rel>
    """

    as_: NotRequired[str]
    """Specifies the type of content being loaded.

    This attribute is required when `rel="preload"` has been set on the `<link>`
    element, optional when `rel="modulepreload"` has been set, and otherwise
    should not be used.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#as>
    """

    crossorigin: NotRequired[Literal["anonymous", "use-credentials"]]
    """Indicates whether CORS must be used when fetching the resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#crossorigin>
    """

    fetchpriority: NotRequired[Literal["high", "low", "auto"]]
    """Provides a hint of the relative priority to use when fetching a preloaded resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#fetchpriority>
    """

    hreflang: NotRequired[str]
    """Indicates the language of the linked resource.

    Note: use only if `href` attribute is present.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#hreflang>
    """

    integrity: NotRequired[str]
    """Inline-metadata to verify that resource has not been manipulated.

    This can be a base64-encoded cryptographic hash of the resource (file) to be
    fetched.

    Note: An integrity value may contain multiple hashes separated by
    whitespace. A resource will be loaded if it matches one of those hashes.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#integrity>
    """

    media: NotRequired[str]
    """Specifies the media that the linked resource applies to.

    Its value must be a media type / media query. This attribute is mainly
    useful when linking to external stylesheets — it allows the user agent to
    pick the best adapted one for the device it runs on.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#media>
    """

    referrerpolicy: NotRequired[
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "unsafe-url",
        ]
    ]
    """Indicates which referrer to use when fetching the resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#referrerpolicy>
    """

    sizes: NotRequired[str]
    """Sizes of the icons for visual media contained in the resource.

    It must be present only if the `rel` contains a value of `icon` or a
    non-standard type such as Apple's `apple-touch-icon`. It may have the
    following values:

        - "any": can be scaled to any size, i.e. `image/svg+xml` format.
        - "<width>x<height>": each size is in pixels, i.e. "200x200".

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#sizes>
    """

    type_: NotRequired[str]
    """Defines the type of the content linked to.

     The value of the attribute should be a MIME type such as text/html,
     text/css, and so on. The common use of this attribute is to define the type
     of stylesheet being referenced (such as text/css), but given that CSS is
     the only stylesheet language used on the web, not only is it possible to
     omit the type attribute, but is actually now recommended practice. It is
     also used on rel="preload" link types, to make sure the browser only
     downloads file types that it supports.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#type>
    """
