from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

SourceElement = NewType("SourceElement", VoidElement)
"""A `<source>` element."""


def source(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[SourceAttrs],
) -> SourceElement:
    """Specifies one or more media resources for the media elements.

    Media elements: `<picture>`, `<audio>`, and `<video>`

    This element is commonly used to offer the same media content in multiple
    file formats in order to provide compatibility with a broad range of
    browsers given their differing support for image file formats and media file
    formats.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source>
    """
    el = VoidElement("source")(**attrs, **extra_attrs or {})
    return SourceElement(el)


class SourceAttrs(GlobalAttrs):
    """Attributes for the `<source>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#attributes>
    """

    type_: NotRequired[str]
    """Specifies the MIME media type of the image or other media type.

    Image types: <https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types>

    Other types: <https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Containers>

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#type>
    """

    src: NotRequired[str]
    """Specifies the URL of the media resource.

    Note: required for `<audio>` or `<video>`, but not allowed if parent is
    `<picture>`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#src>
    """

    srcset: NotRequired[str]
    """Comma-separated list of one or more image URLs and their descriptors.

    Note: required if the parent of `<source>` is `<picture>`, but not allowed
    if parent is `<audio>` or `<video>`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#srcset>
    """

    sizes: NotRequired[str]
    """List of source sizes describing the final rendered width of the image.

    Note: allowed if parent of `<source>` is `<picture>`, but not allowed if parent
    is `<audio>` or `<video>`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#sizes>
    """

    media: NotRequired[str]
    """Specifies the media query for the resource's intended media.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#media>
    """

    height: NotRequired[int]
    """The displayed height of the resource, in CSS pixels.

    Note: allowed if parent of `<source>` is `<picture>`, but not allowed if
    parent is `<audio>` or `<video>`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#height>
    """

    width: NotRequired[int]
    """The displayed width of the resource, in CSS pixels.

    Note: allowed if parent of `<source>` is `<picture>`, but not allowed if
    parent is `<audio>` or `<video>`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/source#width>
    """
