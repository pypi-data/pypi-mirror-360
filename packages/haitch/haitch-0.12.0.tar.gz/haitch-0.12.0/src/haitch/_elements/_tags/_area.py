from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

AreaElement = NewType("AreaElement", VoidElement)
"""An `<area>` element."""


def area(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[AreaAttrs],
) -> AreaElement:
    """Defines an area inside an image map.

    An image map allows geometric areas on an image to be associated with
    hypertext links. This element is used only within a `<map>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area>
    """
    el = VoidElement("area")(**attrs, **extra_attrs or {})
    return AreaElement(el)


class AreaAttrs(GlobalAttrs):
    """Attributes for the `<area>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#attributes>
    """

    alt: NotRequired[str]
    """String alternative to display on browsers that do not display images.

    Note: this attribute is required only if the `href` attribute is used.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#alt>
    """

    coords: NotRequired[str]
    """Coordinates of the `shape` attribute in size, shape, and placement.

    Note: this attribute must not be used when `shape` is set to default.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#coords>
    """

    download: NotRequired[str]
    """Indicates the hyperlink to be used for downloading a resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#download>
    """

    href: NotRequired[str]
    """The hyperlink target URL for the area.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#href>
    """

    ping: NotRequired[str]
    """Space-separated list of URLs to ping when hyperlink followed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#ping>
    """

    rel: NotRequired[str]
    """Defines the relationship between a linked resource and document.

    Valid values: <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel>

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#rel>
    """

    shape: NotRequired[Literal["default", "rect", "circle", "poly"]]
    """The shape of the associated hot spot.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#shape>
    """

    target: NotRequired[str]
    """A keyword of the browsing context to display the linked resource.

    The following keywords have special meaning:

      - `_self` (default): load into same browsing content as current one.
      - `_blank`: load into a new unamed browsing context.
      - `_parent`: load into the parent browsing context.
      - `_top`: load into the top-level browsing context.

    Note: Setting target="_blank" on `<area>` elements implicitly provides the
    same rel behavior as setting rel="noopener" which does not set
    window.opener. See browser compatibility for support status.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/area#target>
    """
