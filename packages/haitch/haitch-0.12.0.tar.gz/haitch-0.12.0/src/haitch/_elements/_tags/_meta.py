from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import VoidElement

MetaElement = NewType("MetaElement", VoidElement)
"""A `<meta>` element."""


def meta(
    *,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[MetaAttrs],
) -> MetaElement:
    """Represents additional metadata that cannot be represented.

    Note: the attribute `name` has a specific meaning for the `<meta>` element,
    and the `itemprop` attribute must not be set on the same `<meta>` element
    that has any existing `name`, `http-equiv` or `charset` attributes.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta>
    """
    el = VoidElement("meta")(**attrs, **extra_attrs or {})
    return MetaElement(el)


class MetaAttrs(GlobalAttrs):
    """Attributes for the `<meta>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#attributes>
    """

    charset: NotRequired[str]
    """Declares the document's character encoding.

    If the attribute is present, its value must be an ASCII case-insensitive
    match for the string "utf-8", because UTF-8 is the only valid encoding for
    HTML5 documents. `<meta>` elements which declare a character encoding must
    be located entirely within the first 1024 bytes of the document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#charset>
    """

    content: NotRequired[str]
    """Contains the valuef for the `http-equiv` or `name` attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#content>
    """

    http_equiv: NotRequired[
        Literal[
            "content-security-policy",
            "content-type",
            "default-style",
            "x-ua-compatible",
            "refresh",
        ]
    ]
    """Defines a pragma directive.

    The attribute is named `http-equiv(alent)` because all the allowed values
    are names of particular HTTP headers.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#http-equiv>
    """

    name: NotRequired[str]
    """Provides metadata in terms of name-value pairs.

    Often used together with `content` where the `name` attribute gives the
    metadata name, and the `content` attributes gives the value.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#name>
    """
