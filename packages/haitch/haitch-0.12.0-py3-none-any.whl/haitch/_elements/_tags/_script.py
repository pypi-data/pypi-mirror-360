from __future__ import annotations

from typing import Literal, NewType, Optional

from typing_extensions import NotRequired, Unpack

from haitch._attrs import Attributes, GlobalAttrs
from haitch._elements._element import Element
from haitch._typing import Child

ScriptElement = NewType("ScriptElement", Element)
"""An `<script>` element."""


def script(
    *children: Child,
    extra_attrs: Optional[Attributes] = None,
    **attrs: Unpack[ScriptAttrs],
) -> ScriptElement:
    """Used to embed executable code or data.

    This is typically used to embed or refer to JavaScript code. The `<script>`
    element can also be used with other languages, such as WebGL's GLSL shader
    programming language and JSON.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script>
    """
    el = Element("script", unsafe=True)(**attrs, **extra_attrs or {})(*children)
    return ScriptElement(el)


class ScriptAttrs(GlobalAttrs):
    """Attributes for the `<script>` element.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#attributes>
    """

    async_: NotRequired[bool]
    """Fetch in parallel to parsing and evaluated as soon as it is available.
    
    For module scripts, if the async attribute is present then the scripts and
    all their dependencies will be fetched in parallel to parsing and evaluated
    as soon as they are available.

    This attribute allows the elimination of parser-blocking JavaScript where
    the browser would have to load and evaluate scripts before continuing to
    parse. `defer` has a similar effect in this case.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#async>
    """

    crossorigin: NotRequired[Literal["anonymous", "use-credentials"]]
    """Indicates whether CORS must be used when fetching the resource.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#crossorigin>
    """

    defer: NotRequired[bool]
    """Indicates to browser that the script is meant to be executed afterwards.

    Concretely, this is after the document has been parsed, but before firing
    `DOMContentLoaded`. Scripts with the `defer` attribute will prevent the
    `DOMContentLoaded` event from firing until the script has loaded and
    finished evaluating.
    
    Warning: This attribute must not be used if the src attribute is absent
    (i.e. for inline scripts), in this case it would have no effect. The defer
    attribute has no effect on module scripts — they defer by default.

    Scripts with the defer attribute will execute in the order in which they
    appear in the document. This attribute allows the elimination of
    parser-blocking JavaScript where the browser would have to load and evaluate
    scripts before continuing to parse. async has a similar effect in this case.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#defer>
    """

    fetchpriority: NotRequired[Literal["high", "low", "auto"]]
    """Provides hint of the relative priority when fetching an external script.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#fetchpriority>
    """

    integrity: NotRequired[str]
    """Contains inline metadata that a user agent can use to verify.

    The goal is to verify that a fetched resource has been delivered free of
    unexpected manipulation.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#integrity>
    """

    nomodule: NotRequired[bool]
    """Indicates that ES modules should not be executed.

    In effect, this can be used to serve fallback scripts to older browsers that
    do not support modular JavaScript code.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#nomodule>
    """

    referrerpolicy: NotRequired[
        Literal[
            "no-referrer",
            "no-referrer-when-downgrade",
            "origin",
            "origin-when-cross-origin",
            "same-origin",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "unsafe-url",
        ]
    ]
    """Indicates which referrer to send when fetching the script.

    Note: An empty string value ("") is both the default value, and a fallback
    value if `referrerpolicy` is not supported. If `referrerpolicy` is not
    explicitly specified on the `<script>` element, it will adopt a higher-level
    referrer policy, i.e. one set on the whole document or domain. If a
    higher-level policy is not available, the empty string is treated as being
    equivalent to `strict-origin-when-cross-origin`.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#referrerpolicy>
    """

    src: NotRequired[str]
    """Specifies the URI of an external script.

    Used as an alternative to embedding a script directly within a document.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#src>
    """

    type_: NotRequired[Literal["", "text/javascript", "importmap", "module"]]
    """Indicates the type of script represented.

    <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script#type>
    """
