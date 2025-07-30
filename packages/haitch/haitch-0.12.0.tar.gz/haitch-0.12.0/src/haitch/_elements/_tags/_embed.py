from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

EmbedElement = NewType("EmbedElement", VoidElement)
"""An `<embed>` element."""


def embed(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[EmbedAttrs],
) -> EmbedElement:
    """Embeds external content at the specified point in the document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed>
    """
    el = VoidElement("embed")(**attrs, **extra_attrs or {})
    return EmbedElement(el)


class EmbedAttrs(GlobalAttrs):
    """Attributes for the `<embed>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed#attributes>
    """

    height: int
    """The displayed height of the resource, in CSS pixels.

    Note: this must be an absolute value; percentages are not allowed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed#height>
    """

    src: str
    """The URL of the resource being embedded.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed#src>
    """

    type_: str
    """The MIME type to use to select the plug-in to instantiate.

    Valid mime types: <https://www.iana.org/assignments/media-types/media-types.xhtml>

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed#type>
    """

    width: int
    """The displayed width of the resource, in CSS pixels.

    Note: this must be an absolute value; percentages are not allowed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/embed#width>
    """
