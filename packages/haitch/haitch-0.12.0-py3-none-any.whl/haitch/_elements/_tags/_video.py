from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

VideoElement = NewType("VideoElement", Element)
"""A `<video>` element."""


def video(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[VideoAttrs],
) -> VideoElement:
    """Embeds a media player which supports video playback.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video>
    """
    el = Element("video")(**attrs, **extra_attrs or {})(*children)
    return VideoElement(el)


class VideoAttrs(GlobalAttrs):
    """Attributes for the `<video>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#attributes>
    """

    autoplay: NotRequired[bool]
    """Video automatically begins playing as soon as it can.

    Note: modern browsers block this attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#autoplay>
    """

    controls: NotRequired[bool]
    """Offer controls to allow the user to control playback.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#controls>
    """

    controlslist: NotRequired[Literal["nodownload", "nofullscreen", "noremoteplay"]]
    """Helps the browser select which controls to show.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#controlslist>
    """

    crossorigin: NotRequired[Literal["anonymous", "use-credentials"]]
    """Indicates whether CORS must be used when fetching the resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#crossorigin>
    """

    disablepictureinpicture: NotRequired[bool]
    """Prevents browser from suggesting Picture-in-Picture context menu.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#disablepictureinpicture>
    """

    disableremoteplayback: NotRequired[bool]
    """Disables capability of remote playback.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#disableremoteplayback>
    """

    height: NotRequired[int]
    """The height of the video's display area in CSS pixels.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#height>
    """

    loop: NotRequired[bool]
    """Automatically seek back to hte start upon reaching the end of the video.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#loop>
    """

    muted: NotRequired[bool]
    """Indicates whether the audio will be initially silenced.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#muted>
    """

    playsinline: NotRequired[bool]
    """Indicates the video will be played within the element's playback area.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#playsinline>
    """

    poster: NotRequired[str]
    """A URL for an image to be shown while the video is downloading.

    If not specified the first frame is shown as the poster frame.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#poster>
    """

    preload: NotRequired[Literal["none", "metadata", "auto"]]
    """Provides hint to browser for best user experience.

    - `none`: don't fetch anything.
    - `metadata`: fetch video metadata, i.e. length.
    - `auto`: always download the entire video file.

    The spec advises to set to this attribute to `metadata`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#preload>
    """

    src: NotRequired[str]
    """A URL of the video to embed.

    You may instead use the `source` element within the video block to specify
    the video to embed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#src>
    """

    width: NotRequired[int]
    """The width of the video's display area in CSS pixels.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video#width>
    """
