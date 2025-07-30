from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_table(snapshot: Snapshot) -> None:
    dom = H.table(
        H.caption("Employee information"),
        H.colgroup(
            H.col(span=2),
        ),
        H.thead(
            H.tr(
                H.th("Name"),
                H.th("Age"),
            )
        ),
        H.tbody(
            H.tr(
                H.td("Maria Sanchez"),
                H.td("28"),
            ),
            H.tr(
                H.td("Michael Johnson"),
                H.td("34"),
            ),
        ),
        H.tfoot(
            H.tr(
                H.th("Average"),
                H.td("31"),
            )
        ),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
