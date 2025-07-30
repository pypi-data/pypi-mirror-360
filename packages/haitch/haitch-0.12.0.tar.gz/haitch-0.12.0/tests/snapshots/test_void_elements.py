from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_void_elements(snapshot: Snapshot) -> None:
    dom = H.fragment(
        H.map(name="kreis")(
            H.area(
                shape="circle",
                coords="75,75,75",
                href="left.html",
                alt="Click to go left",
            ),
        ),
        H.base(href="https://www.example.com/"),
        H.embed(type_="video/mp4", src="flower.mp4", height=250, width=250),
        H.p("Fernstraßen", H.wbr(), "bau"),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
