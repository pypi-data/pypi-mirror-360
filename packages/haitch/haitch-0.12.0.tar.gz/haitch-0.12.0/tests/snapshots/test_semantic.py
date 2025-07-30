from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_semantic(snapshot: Snapshot) -> None:
    dom = H.fragment(
        H.header(
            H.h1("Heading"),
            H.nav(
                H.ul(
                    H.li(H.a(href="/")("Home")),
                    H.li(H.a(href="/about")("About")),
                ),
            ),
        ),
        H.main(
            H.hgroup(
                H.h1("Semantic HTML"),
                H.p("This showcases some semantic elements."),
            ),
            H.aside(
                H.blockquote("Hello, world!"),
                H.cite("Said all programmers at one point."),
                H.small("This is some information in an aside element."),
                H.menu(
                    H.li("Menu item #1"),
                    H.li("Menu item #2"),
                ),
            ),
            H.section(
                H.h2("Subheading"),
                H.article(
                    "This is an ",
                    H.span(class_="highlight")("article"),
                ),
                H.details(open=True)(
                    H.summary("You can collapse me."),
                ),
            ),
        ),
        H.footer("Footer"),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
