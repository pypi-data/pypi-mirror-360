from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

BaseElement = NewType("BaseElement", VoidElement)
"""A `<base>` element."""


def base(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[BaseAttrs],
) -> BaseElement:
    """Specifies the base URL to use for all relative URLs in a document.

    Note: there can only be one `<base>` element in a document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base>
    """
    el = VoidElement("base")(**attrs, **extra_attrs or {})
    return BaseElement(el)


class BaseAttrs(GlobalAttrs):
    """Attributes for the `<base>` element.

    Warning: A `<base>` element must have an `href` attribute, a target
    attribute, or both. If at least one of these attributes are specified, the
    `<base>` element must come before other elements with attribute values that
    are URLs, such as a `<link>`'s `href` attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base#attributes>
    """

    href: NotRequired[str]
    """The base URL to be used throughout the document for relative URLs.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base#href>
    """

    target: NotRequired[str]
    """A keyword or author-defined name of default browsing context to display.

    The following keywords have special meaning:

      - `_self` (default): load into same browsing content as current one.
      - `_blank`: load into a new unamed browsing context.
      - `_parent`: load into the parent browsing context.
      - `_top`: load into the top-level browsing context.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base#target>
    """
