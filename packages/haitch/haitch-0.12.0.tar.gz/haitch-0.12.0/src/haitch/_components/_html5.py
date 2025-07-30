from typing import Iterable

from haitch._elements._element import Element
from haitch._elements._tags._body import body
from haitch._elements._tags._head import head
from haitch._elements._tags._html import html
from haitch._elements._tags._link import LinkElement
from haitch._elements._tags._meta import meta
from haitch._elements._tags._script import ScriptElement
from haitch._elements._tags._title import title
from haitch._typing import SupportsHtml


def html5(
    *,
    content: SupportsHtml,
    page_title: str = "",
    language_code: str = "",
    body_classes: str = "",
    links: Iterable[LinkElement] = (),
    scripts: Iterable[ScriptElement] = (),
) -> Element:
    """Base HTML5 document container.

    DEPRECATED: this component will not be shipped with the v1 release!
    """
    return html(lang=language_code)(
        head(
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            meta(http_equiv="x-ua-compatible", content="ie=edge"),
            page_title and title(page_title),
            links,
            scripts,
        ),
        body(class_=body_classes)(content) if body_classes else body(content),
    )
