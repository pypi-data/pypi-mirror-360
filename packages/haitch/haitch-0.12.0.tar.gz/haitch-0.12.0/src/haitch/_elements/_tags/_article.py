from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ArticleElement = NewType("ArticleElement", Element)
"""An `<article>` element."""


def article(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> ArticleElement:
    """Represents self-contained composition.

    This can occur in a document, page, application, or site.

    The `<article>` element is intended to be independently distributable or
    reusable (e.g., in syndication). Examples include: a forum post, a magazine
    or newspaper article, or a blog entry, a product card, a user-submitted
    comment, an interactive widget or gadget, or any other independent item of
    content.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/article>
    """
    el = Element("article")(**attrs, **extra_attrs or {})(*children)
    return ArticleElement(el)
