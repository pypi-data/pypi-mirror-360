"""
haitch - simplify your HTML building.
=====================================

Import haitch like so:

>>> import haitch as H

Now you have access to any element you like:

>>> H.img(src="my-image.png", alt="cool image") # valid
>>> H.foo("Custom element!") # valid

Both these statements would render correctly; however, the `<img>`
element would have typing and documentation, while the `<foo>` one
would not because it is not a standard element.

Lazily build a dom tree by passing children (args) and/or
attributes (kwargs):

>>> dom = H.a(
...     H.strong("Check out my website"), # arg
...     href="https://example.com", # kwarg
... )

A called element validates its input, attaches the values to itself,
and then returns itself. This enables us to chain calls together:

>>> dom = H.a(href="https://example.com")(
...     H.strong("Check out my website"),
... )

Both instances of `dom` will render the same HTML. I prefer the second
way because it looks more like HTML, and it keeps the attributes closer
to the parent element.

Until now we have only lazily built the dom tree. In order to render it
to HTML, you need to invoke the underlying `__str__` method:

>>> str(dom) # or print(dom)
<a href="https://example.com">
  <strong>Check out my website</strong>
</a>
"""

from haitch._components._html5 import html5
from haitch._elements._element import Element, VoidElement
from haitch._elements._special._fragment import fragment
from haitch._elements._special._unsafe import unsafe
from haitch._elements._tags._a import AnchorElement, a
from haitch._elements._tags._abbr import AbbrElement, abbr
from haitch._elements._tags._address import AddressElement, address
from haitch._elements._tags._area import AreaElement, area
from haitch._elements._tags._article import ArticleElement, article
from haitch._elements._tags._aside import AsideElement, aside
from haitch._elements._tags._audio import AudioElement, audio
from haitch._elements._tags._b import BElement, b
from haitch._elements._tags._base import BaseElement, base
from haitch._elements._tags._bdi import BdiElement, bdi
from haitch._elements._tags._bdo import BdoElement, bdo
from haitch._elements._tags._blockquote import BlockquoteElement, blockquote
from haitch._elements._tags._body import BodyElement, body
from haitch._elements._tags._br import BrElement, br
from haitch._elements._tags._button import ButtonElement, button
from haitch._elements._tags._canvas import CanvasElement, canvas
from haitch._elements._tags._caption import CaptionElement, caption
from haitch._elements._tags._cite import CiteElement, cite
from haitch._elements._tags._code import CodeElement, code
from haitch._elements._tags._col import ColElement, col
from haitch._elements._tags._colgroup import ColgroupElement, colgroup
from haitch._elements._tags._data import DataElement, data
from haitch._elements._tags._datalist import DatalistElement, datalist
from haitch._elements._tags._dd import DescriptionDefinitionElement, dd
from haitch._elements._tags._del import DelElement, del_
from haitch._elements._tags._details import DetailsElement, details
from haitch._elements._tags._dialog import DialogElement, dialog
from haitch._elements._tags._div import DivElement, div
from haitch._elements._tags._dl import DescriptionListElement, dl
from haitch._elements._tags._dt import DescriptionTermElement, dt
from haitch._elements._tags._em import EmElement, em
from haitch._elements._tags._embed import EmbedElement, embed
from haitch._elements._tags._fieldset import FieldsetElement, fieldset
from haitch._elements._tags._figcaption import FigcaptionElement, figcaption
from haitch._elements._tags._figure import FigureElement, figure
from haitch._elements._tags._footer import FooterElement, footer
from haitch._elements._tags._form import FormElement, form
from haitch._elements._tags._h1 import H1Element, h1
from haitch._elements._tags._h2 import H2Element, h2
from haitch._elements._tags._h3 import H3Element, h3
from haitch._elements._tags._h4 import H4Element, h4
from haitch._elements._tags._h5 import H5Element, h5
from haitch._elements._tags._h6 import H6Element, h6
from haitch._elements._tags._head import HeadElement, head
from haitch._elements._tags._header import HeaderElement, header
from haitch._elements._tags._hgroup import HgroupElement, hgroup
from haitch._elements._tags._hr import HrElement, hr
from haitch._elements._tags._html import HtmlElement, html
from haitch._elements._tags._i import IElement, i
from haitch._elements._tags._img import ImgElement, img
from haitch._elements._tags._input import InputElement, input
from haitch._elements._tags._ins import InsElement, ins
from haitch._elements._tags._kbd import KbdElement, kbd
from haitch._elements._tags._label import LabelElement, label
from haitch._elements._tags._legend import LegendElement, legend
from haitch._elements._tags._li import LiElement, li
from haitch._elements._tags._link import LinkElement, link
from haitch._elements._tags._main import MainElement, main
from haitch._elements._tags._map import MapElement, map
from haitch._elements._tags._mark import MarkElement, mark
from haitch._elements._tags._menu import MenuElement, menu
from haitch._elements._tags._meta import MetaElement, meta
from haitch._elements._tags._meter import MeterElement, meter
from haitch._elements._tags._nav import NavElement, nav
from haitch._elements._tags._noscript import NoscriptElement, noscript
from haitch._elements._tags._object import ObjectElement, object
from haitch._elements._tags._ol import OlElement, ol
from haitch._elements._tags._optgroup import OptgroupElement, optgroup
from haitch._elements._tags._option import OptionElement, option
from haitch._elements._tags._output import OutputElement, output
from haitch._elements._tags._p import ParagraphElement, p
from haitch._elements._tags._picture import PictureElement, picture
from haitch._elements._tags._pre import PreElement, pre
from haitch._elements._tags._progress import ProgressElement, progress
from haitch._elements._tags._q import QuoteElement, q
from haitch._elements._tags._rp import RubyParenthesesElement, rp
from haitch._elements._tags._rt import RubyTextElement, rt
from haitch._elements._tags._ruby import RubyElement, ruby
from haitch._elements._tags._s import StrikethroughElement, s
from haitch._elements._tags._samp import SampElement, samp
from haitch._elements._tags._script import ScriptElement, script
from haitch._elements._tags._search import SearchElement, search
from haitch._elements._tags._section import SectionElement, section
from haitch._elements._tags._select import SelectElement, select
from haitch._elements._tags._slot import SlotElement, slot
from haitch._elements._tags._small import SmallElement, small
from haitch._elements._tags._source import SourceElement, source
from haitch._elements._tags._span import SpanElement, span
from haitch._elements._tags._strong import StrongElement, strong
from haitch._elements._tags._style import StyleElement, style
from haitch._elements._tags._sub import SubElement, sub
from haitch._elements._tags._summary import SummaryElement, summary
from haitch._elements._tags._sup import SupElement, sup
from haitch._elements._tags._table import TableElement, table
from haitch._elements._tags._tbody import TbodyElement, tbody
from haitch._elements._tags._td import TdElement, td
from haitch._elements._tags._template import TemplateElement, template
from haitch._elements._tags._textarea import TextareaElement, textarea
from haitch._elements._tags._tfoot import TfootElement, tfoot
from haitch._elements._tags._th import ThElement, th
from haitch._elements._tags._thead import TheadElement, thead
from haitch._elements._tags._time import TimeElement, time
from haitch._elements._tags._title import TitleElement, title
from haitch._elements._tags._tr import TrElement, tr
from haitch._elements._tags._track import TrackElement, track
from haitch._elements._tags._u import UElement, u
from haitch._elements._tags._ul import UlElement, ul
from haitch._elements._tags._var import VarElement, var
from haitch._elements._tags._video import VideoElement, video
from haitch._elements._tags._wbr import WbrElement, wbr
from haitch._typing import Child, Html, SupportsHtml

__all__ = [
    "AbbrElement",
    "AddressElement",
    "AnchorElement",
    "AreaElement",
    "ArticleElement",
    "AsideElement",
    "AudioElement",
    "BElement",
    "BaseElement",
    "BdiElement",
    "BdoElement",
    "BlockquoteElement",
    "BodyElement",
    "BrElement",
    "ButtonElement",
    "CanvasElement",
    "CaptionElement",
    "Child",
    "CiteElement",
    "CodeElement",
    "ColElement",
    "ColgroupElement",
    "DataElement",
    "DatalistElement",
    "DelElement",
    "DescriptionDefinitionElement",
    "DescriptionListElement",
    "DescriptionTermElement",
    "DetailsElement",
    "DialogElement",
    "DivElement",
    "Element",
    "EmElement",
    "EmbedElement",
    "FieldsetElement",
    "FigcaptionElement",
    "FigureElement",
    "FooterElement",
    "FormElement",
    "FormElement",
    "H1Element",
    "H2Element",
    "H3Element",
    "H4Element",
    "H5Element",
    "H6Element",
    "HeadElement",
    "HeaderElement",
    "HgroupElement",
    "HrElement",
    "Html",
    "HtmlElement",
    "IElement",
    "ImgElement",
    "InputElement",
    "InsElement",
    "KbdElement",
    "LabelElement",
    "LegendElement",
    "LiElement",
    "LinkElement",
    "MainElement",
    "MapElement",
    "MarkElement",
    "MenuElement",
    "MetaElement",
    "MeterElement",
    "NavElement",
    "NoscriptElement",
    "ObjectElement",
    "OlElement",
    "OptgroupElement",
    "OptionElement",
    "OutputElement",
    "ParagraphElement",
    "PictureElement",
    "PreElement",
    "ProgressElement",
    "QuoteElement",
    "RubyElement",
    "RubyParenthesesElement",
    "RubyTextElement",
    "SampElement",
    "ScriptElement",
    "SearchElement",
    "SectionElement",
    "SelectElement",
    "SlotElement",
    "SmallElement",
    "SourceElement",
    "SpanElement",
    "StrikethroughElement",
    "StrongElement",
    "StyleElement",
    "SubElement",
    "SummaryElement",
    "SupElement",
    "SupportsHtml",
    "TableElement",
    "TbodyElement",
    "TdElement",
    "TemplateElement",
    "TextareaElement",
    "TfootElement",
    "ThElement",
    "TheadElement",
    "TimeElement",
    "TitleElement",
    "TrElement",
    "TrackElement",
    "UElement",
    "UlElement",
    "VarElement",
    "VideoElement",
    "VoidElement",
    "WbrElement",
    "a",
    "abbr",
    "address",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "bdi",
    "bdo",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "datalist",
    "dd",
    "del_",
    "details",
    "dialog",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "form",
    "fragment",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hgroup",
    "hr",
    "html",
    "html5",
    "i",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "menu",
    "meta",
    "meter",
    "nav",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "picture",
    "pre",
    "progress",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "script",
    "search",
    "section",
    "select",
    "slot",
    "small",
    "source",
    "span",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "u",
    "ul",
    "unsafe",
    "var",
    "video",
    "wbr",
]


def __getattr__(tag: str) -> Element:
    return Element(tag)
