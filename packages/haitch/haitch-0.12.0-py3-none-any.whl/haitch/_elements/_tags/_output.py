from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

OutputElement = NewType("OutputElement", Element)
"""An `<output>` element."""


def output(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[OutputAttrs],
) -> OutputElement:
    """Container element to inject results.

    Results could be a calculation injected by the site/app or the outcome of a
    user action.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output>
    """
    el = Element("output")(**attrs, **extra_attrs or {})(*children)
    return OutputElement(el)


class OutputAttrs(GlobalAttrs):
    """Attributes for the `<output>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output#attributes>
    """

    for_: NotRequired[str]
    """Space-separated list of other element IDs.

    This indicates that those elements contributed input values to (or otherwise
    affected) the calculation.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output#for>
    """

    form: NotRequired[str]
    """A form ID to associate the output its form owner.

    This allows you to associate results anywhere in the document, not just
    inside a `form` element.

    Note: name and content are not submitted when the form is submitted.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output#form>
    """

    name: NotRequired[str]
    """The element's name used in the form element's API.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/output#name>
    """
