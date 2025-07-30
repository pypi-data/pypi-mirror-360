from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_components(snapshot: Snapshot) -> None:
    dom = H.html5(
        content=H.fragment(
            H.header(
                H.h1("Hello, reader."),
            ),
            H.main(
                H.section(
                    H.p("So why is this a cool page?"),
                    H.a(href="#")("Check the link for more info!"),
                ),
            ),
        ),
        page_title="Cool page",
        language_code="en",
        body_classes="container box",
        links=[
            H.link(href="main.css", rel="stylesheet"),
            H.link(href="custom.css", rel="stylesheet"),
        ],
        scripts=[
            H.script(src="main.js", defer=True),
        ],
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
