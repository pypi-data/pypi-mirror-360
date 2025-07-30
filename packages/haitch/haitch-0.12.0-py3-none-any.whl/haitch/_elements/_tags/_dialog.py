from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

DialogElement = NewType("DialogElement", Element)
"""A `<dialog>` element."""


def dialog(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[DialogAttrs],
) -> DialogElement:
    """Represents a modal or non-modal dialog box or interactive component.

    This can be a dismissible alert, inspector, or subwindow. Modal dialog boxes
    interrupt interaction with the rest of the page being inert, while non-modal
    boxes allow interactions with the rest of the page.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog>
    """
    el = Element("dialog")(**attrs, **extra_attrs or {})(*children)
    return DialogElement(el)


class DialogAttrs(GlobalAttrs):
    """Attributes for the `<dialog>` element.

    Warning: the global `tabindex` attribute must not be used.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog#attributes>
    """

    open: NotRequired[bool]
    """Indicates that the dialog box is active and available for interaction.

    It is recommended to use `.show()` or `.showModal()` method to render
    dialogs, rather than the `open` attribute. If a `dialog` element is opened
    using the `open` attribute, it is non-modal.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog#open>
    """
