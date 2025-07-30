from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

SummaryElement = NewType("SummaryElement", Element)
"""A `<summary>` element."""


def summary(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> SummaryElement:
    """Specifies a summary, caption, or legend for a `<details>` element.

    Clicking the `<summary>` element toggles the state of the parent `<details>`
    element open and closed.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/summary>
    """
    el = Element("summary")(**attrs, **extra_attrs or {})(*children)
    return SummaryElement(el)
