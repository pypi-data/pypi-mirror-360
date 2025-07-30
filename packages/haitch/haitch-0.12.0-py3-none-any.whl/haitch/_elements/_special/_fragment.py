from haitch._elements._element import Element
from haitch._typing import Child


def fragment(*children: Child) -> Element:
    """Accepts only children as input and does not wrap its parent tag."""
    return Element("fragment")(*children)
