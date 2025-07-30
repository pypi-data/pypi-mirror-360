from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

AudioElement = NewType("AudioElement", Element)
"""An `<audio>` element."""


def audio(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[AudioAttrs],
) -> AudioElement:
    """Embeds sound content in documents.

    It may contain one or more audio sources, represented using the `src`
    attribute or the `<source>` element: the browser will choose the most
    suitable one. It can also be the destination for streamed media, using a
    `MediaStream`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio>
    """
    el = Element("audio")(**attrs, **extra_attrs or {})(*children)
    return AudioElement(el)


class AudioAttrs(GlobalAttrs):
    """Attributes for the `<audio>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#attributes>
    """

    autoplay: NotRequired[bool]
    """Starts the playback as soon as it can do so.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#autoplay>
    """

    controls: NotRequired[bool]
    """Offer controls to allow control over audio playback.

    This can include volume, seeking, and pause/resume.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#controls>
    """

    controlslist: NotRequired[Literal["nodownload", "nofullscreen", "noremoteplayback"]]
    """Helps the browser select what controls to show.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#controlslist>
    """

    crossorigin: NotRequired[Literal["anonymous", "use-credentials"]]
    """Indicates whether CORS must be used when fetching the resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#crossorigin>
    """

    disableremoteplayback: NotRequired[bool]
    """Disable the capability of remote playback.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#disableremoteplayback>
    """

    loop: NotRequired[bool]
    """Automatically seek back to the start upon finishing.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#loop>
    """

    muted: NotRequired[bool]
    """Indicates whether the audio will be initially silenced.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#muted>
    """

    preload: NotRequired[Literal["none", "metadata", "auto"]]
    """Provides hint to browser for best user experience.

    - `none`: don't fetch anything.
    - `metadata`: fetch audio metadata, i.e. length.
    - `auto`: always download the entire audio file.

    The spec advises to set to this attribute to `metadata`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#preload>
    """

    src: NotRequired[str]
    """The URL of the audio to embed.

    You may instead opt for the `<source>` within the audio block instead.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#src>
    """
