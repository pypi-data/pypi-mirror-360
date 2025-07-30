from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

TemplateElement = NewType("TemplateElement", Element)
"""A `<template>` element."""


def template(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[TemplateAttrs],
) -> TemplateElement:
    """Serves as a mechanism for holding HTML fragments.

    These can then either be used later via JavaScript or generated immediately
    into shadow DOM.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template>
    """
    el = Element("template")(**attrs, **extra_attrs or {})(*children)
    return TemplateElement(el)


class TemplateAttrs(GlobalAttrs):
    """Attributes for the `<template>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template#attributes>
    """

    shadowrootmode: NotRequired[Literal["open", "closed"]]
    """Creates a shadow root for the parent element.

      - `open`: exposes internal shadow root DOM for JavaScript (recommended).
      - `closed`: hides the internal shadow root DOM from JavaScript.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template#shadowrootmode>
    """

    shadowrootclonable: NotRequired[bool]
    """Set the `clonable` property using this element to `true`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template#shadowrootclonable>
    """

    shadowrootdelegatefocus: NotRequired[bool]
    """Set the `delegateFocus` property using this element to `true`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/template#shadowrootdelegatefocus>
    """
