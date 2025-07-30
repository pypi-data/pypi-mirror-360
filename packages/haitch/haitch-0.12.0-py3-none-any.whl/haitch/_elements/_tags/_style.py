from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

StyleElement = NewType("StyleElement", Element)
"""An `<style>` element."""


def style(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[StyleAttrs],
) -> StyleElement:
    """Contains style information for (part of) document.

    The `<style>` element must be included inside the `<head>` of the document.
    In general, it is better to put your styles in external stylesheets and
    apply them using `<link>` elements.

    Note: if you include multiple `<style>` and `<link>` elements in your
    document, they will be applied to the DOM in the order they are included in
    the document — make sure you include them in the correct order, to avoid
    unexpected cascade issues.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style>
    """
    el = Element("style")(**attrs, **extra_attrs or {})(*children)
    return StyleElement(el)


class StyleAttrs(GlobalAttrs):
    """Attributes for the `<style>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style#attributes>
    """

    media: NotRequired[str]
    """Defines which media the style should be applied to.

    Its value is a media query, defaults to `all` if the attribute is missing.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/style#media>
    """
