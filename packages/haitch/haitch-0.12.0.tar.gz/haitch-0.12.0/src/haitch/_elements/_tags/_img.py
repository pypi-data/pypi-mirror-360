from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

ImgElement = NewType("ImgElement", VoidElement)
"""An `<img>` element."""


def img(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ImgAttrs],
) -> ImgElement:
    """Embeds an image into the document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img>
    """
    el = VoidElement("img")(**attrs, **extra_attrs or {})
    return ImgElement(el)


class ImgAttrs(GlobalAttrs):
    """Attributes for the `<img>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#attributes>
    """

    src: str
    """Contains the path to the image you want to embed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#src>
    """

    alt: NotRequired[str]
    """Holds a textual replacement for the image.

    Note: Browsers do not always display images. There are a number of
    situations in which a browser might not display images, such as:

        - Non-visual browsers
        - The user chooses not to display images
        - The image is invalid or an unsupported type

    In these cases, the browser may replace the image with the text in the
    element's alt attribute. For these reasons and others, provide a useful
    value for alt whenever possible.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#alt>
    """

    crossorigin: NotRequired[Literal["anonymous", "use-credentials"]]
    """Indicates if the fetching of the image must be done using a CORS request.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#crossorigin>
    """

    decoding: NotRequired[Literal["sync", "async", "auto"]]
    """Hint to the browser as to whether it should perform image decoding.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#decoding>
    """

    elementtiming: NotRequired[str]
    """Marks the image for observation by the PerformanceElementTiming API.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#elementtiming>
    """

    fetchpriority: NotRequired[Literal["high", "low", "auto"]]
    """Provides a hint of the relative priority to use when fetching the image.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#fetchpriority>
    """

    height: NotRequired[int]
    """The intrinsic height of the image in pixels.

    Note: Including height and width enables the aspect ratio of the image to be
    calculated by the browser prior to the image being loaded. This aspect ratio
    is used to reserve the space needed to display the image, reducing or even
    preventing a layout shift when the image is downloaded and painted to the
    screen. Reducing layout shift is a major component of good user experience
    and web performance.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#height>
    """

    ismap: NotRequired[bool]
    """Indicates that the image is part of a server-side map.

    Note: This attribute is allowed only if the `<img>` element is a descendant
    of an `<a>` element with a valid href attribute. This gives users without
    pointing devices a fallback destination.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#ismap>
    """

    loading: NotRequired[Literal["eager", "lazy"]]
    """Indicates how the browser should load the image.

    Note: Loading is only deferred when JavaScript is enabled. This is an
    anti-tracking measure, because if a user agent supported lazy loading when
    scripting is disabled, it would still be possible for a site to track a
    user's approximate scroll position throughout a session, by strategically
    placing images in a page's markup such that a server can track how many
    images are requested and when.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#loading>
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
    """String indicating which referrer to use when fetching the resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#referrerpolicy>
    """

    sizes: NotRequired[str]
    """Indicates a set of source sizes.

    The value is one or more strings separated by commas.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#sizes>
    """

    srcset: NotRequired[str]
    """Indicates possible image sources for the user agent to use.
    
    Value is one or more strings separated by commas.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#srcset>
    """

    width: NotRequired[int]
    """The intrinsic width of the image in pixels.

    Note: Including height and width enables the aspect ratio of the image to be
    calculated by the browser prior to the image being loaded. This aspect ratio
    is used to reserve the space needed to display the image, reducing or even
    preventing a layout shift when the image is downloaded and painted to the
    screen. Reducing layout shift is a major component of good user experience
    and web performance.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#width>
    """

    usemap: NotRequired[str]
    """The partial URL of an image map associated with the element.

    Value must start with #.

    Note: You cannot use this attribute if the `<img>` element is inside an `<a>` or
    `<button>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img#usemap>
    """
