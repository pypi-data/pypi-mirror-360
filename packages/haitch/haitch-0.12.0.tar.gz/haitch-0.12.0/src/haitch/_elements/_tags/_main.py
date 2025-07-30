from __future__ import annotations

from typing import NewType, Optional

from typing_extensions import Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

MainElement = NewType("MainElement", Element)
"""A `<main>` element."""


def main(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[GlobalAttrs],
) -> MainElement:
    """Represents the dominant content of the `<body>` of a document.

    The main content area consists of content that is directly related to or
    expands upon the central topic of a document, or the central functionality
    of an application.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/main>
    """
    el = Element("main")(**attrs, **extra_attrs or {})(*children)
    return MainElement(el)
