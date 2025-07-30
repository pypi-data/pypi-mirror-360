from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

AbbrElement = NewType("AbbrElement", Element)
"""An `<abbr>` element."""


def abbr(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> AbbrElement:
    """Represents an abbreviation or acronym.

    When including an abbreviation or acronym, provide a full expansion of the
    term in plain text on first use, along with the `<abbr>` to mark up the
    abbreviation. This informs the user what the abbreviation or acronym means.

    The optional `title` attribute can provide an expansion for the abbreviation
    or acronym when a full expansion is not present. This provides a hint to
    user agents on how to announce/display the content while informing all users
    what the abbreviation means. If present, title must contain this full
    description and nothing else.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/abbr>
    """
    el = Element("abbr")(**attrs, **extra_attrs or {})(*children)
    return AbbrElement(el)
