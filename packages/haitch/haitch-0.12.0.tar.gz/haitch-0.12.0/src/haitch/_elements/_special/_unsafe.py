from haitch._elements._element import Element


def unsafe(html: str) -> Element:
    """Creates a fragment element with unescaped HTML."""
    return Element("fragment", unsafe=True)(html)
