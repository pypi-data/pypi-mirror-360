from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_headings(snapshot: Snapshot) -> None:
    dom = H.fragment(
        H.h1("Heading 1"),
        H.h2("Heading 2"),
        H.h3("Heading 3"),
        H.h4("Heading 4"),
        H.h5("Heading 5"),
        H.h6("Heading 6"),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
