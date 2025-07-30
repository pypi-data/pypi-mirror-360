from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

TrackElement = NewType("TrackElement", VoidElement)
"""A `<track>` element."""


def track(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[TrackAttrs],
) -> TrackElement:
    """Embeds timed text tracks.

    A common example is to automatically handle subtitles. The tracks are
    formatted in Web Video Text Tracks (WebVTT) format (`.vtt` files).

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track>
    """
    el = VoidElement("track")(**attrs, **extra_attrs or {})
    return TrackElement(el)


class TrackAttrs(GlobalAttrs):
    """Attributes for the `<track>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#attributes>
    """

    src: str
    """Address of the track (`.vtt` file).

    Note: must be a valid URL. This attribute must be specified and its URL
    value must have the same origin as the document - unless the `<audio>` or
    `<video>` parent element of the `track` element has a `crossorigin`
    attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#src>
    """

    default: NotRequired[bool]
    """Indicates that the track should be enabled.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#default>
    """

    kind: NotRequired[
        Literal[
            "subtitles",
            "captions",
            "descriptions",
            "chapters",
            "metadata",
        ]
    ]
    """Indicates how the text track is meant to be used.

    If omitted, the default kind is `subtitles`. If the value is invalid,
    `metadata` will be used.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#kind>
    """

    label: NotRequired[str]
    """User-readable title used by browser when listing available text tracks.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#label>
    """

    srclang: NotRequired[str]
    """Language of the track text data.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/track#srclang>
    """
