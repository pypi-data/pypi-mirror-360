from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ProgressElement = NewType("ProgressElement", Element)
"""A `<progress>` element."""


def progress(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ProgressAttrs],
) -> ProgressElement:
    """Displays an indicator showing the completion progress of a task.

    This is typically dislayed as a progress bar.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress>
    """
    el = Element("progress")(**attrs, **extra_attrs or {})(*children)
    return ProgressElement(el)


class ProgressAttrs(GlobalAttrs):
    """Attributes for the `<progress>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress#attributes>
    """

    max: NotRequired[str]
    """Describes how much work the task requires (default: 1). 

    Note: must be a valid floating point number between 0 and 1.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress#max>
    """

    value: NotRequired[str]
    """Specifies how much of the task has been completed.

    Note: must be a valid floating point number between 0 and `max`. If omitted,
    the progress bar is indeterminate; this indicates that an activity is
    ongoing with no indication of how long it is expected to take.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/progress#value>
    """
