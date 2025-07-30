from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ThElement = NewType("ThElement", Element)
"""A `<th>` element."""


def th(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ThAttrs],
) -> ThElement:
    """Defines a cell as the header of a group of table cells.

    This group is defined by the `scope` and `headers` attribute.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th>
    """
    el = Element("th")(**attrs, **extra_attrs or {})(*children)
    return ThElement(el)


class ThAttrs(GlobalAttrs):
    """Attributes for the `<th>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th#attributes>
    """

    abbr: NotRequired[str]
    """A short, abbreviated description of the header cell's content.

    It is provided as an alternative label to use for the header cell when
    referencing the cell in other contexts. Some user-agents, such as speech
    readers, may present this description before the content itself.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th#abbr>
    """

    colspan: NotRequired[int]
    """A non-negative integer value indicating the number of columns.

    If not provided, the default value is `1`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th#colspan>
    """

    headers: NotRequired[str]
    """Provides the headers for this header cell.

    A list of space-separated strings corresponding to the `id` attributes of
    the `<th>` elements.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th#headers>
    """

    rowspan: NotRequired[int]
    """A non-negative integer value indicating the number of rows.

    If not provided, the default value is `1`. if its value is set to 0, the
    header cell will extends to the end of the table grouping section (<thead>,
    <tbody>, <tfoot>, even if implicitly defined), that the <th> belongs to.
    Values higher than 65534 are clipped at 65534.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th#rowspan>
    """

    scope: NotRequired[Literal["row", "col", "rowgroup", "colgroup"]]
    """Defines the cells that the header element relates to.

    If the `scope` attribute is not specified, or its value is not `row`, `col`,
    `rowgroup`, or `colgroup`, then browsers automatically select the set of
    cells to which the header cell applies.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th#scope>
    """
