from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

HtmlElement = NewType("HtmlElement", Element)
"""A `<html>` element."""


def html(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> HtmlElement:
    """Represents the root of an HTML document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/html>
    """
    prefix = "<!doctype html>"
    el = Element("html", prefix=prefix)(**attrs, **extra_attrs or {})(*children)
    return HtmlElement(el)
